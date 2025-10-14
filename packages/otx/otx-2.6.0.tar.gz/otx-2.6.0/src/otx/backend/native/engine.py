# Copyright (C) 2024-2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""OTX Engine."""

from __future__ import annotations

import copy
import csv
import inspect
import logging
import os
import time
from contextlib import contextmanager
from multiprocessing import Value
from pathlib import Path
from pickle import UnpicklingError  # nosec B403: UnpicklingError is used only for exception handling
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Iterable, Iterator, Literal
from warnings import warn

import torch
from lightning import Trainer, seed_everything
from lightning.pytorch.callbacks import LearningRateMonitor, ModelCheckpoint, RichModelSummary, RichProgressBar
from lightning.pytorch.loggers import CSVLogger, TensorBoardLogger
from lightning.pytorch.plugins.precision import MixedPrecision

from otx.backend.native.callbacks.adaptive_train_scheduling import AdaptiveTrainScheduling
from otx.backend.native.callbacks.aug_scheduler import AugmentationSchedulerCallback
from otx.backend.native.callbacks.gpu_mem_monitor import GPUMemMonitor
from otx.backend.native.callbacks.iteration_timer import IterationTimer
from otx.backend.native.models.base import DataInputParams, OTXModel
from otx.backend.native.tools import adapt_batch_size
from otx.backend.native.utils.cache import TrainerArgumentsCache
from otx.config.device import DeviceConfig
from otx.config.explain import ExplainConfig
from otx.data.module import OTXDataModule
from otx.engine.engine import Engine
from otx.tools.auto_configurator import DEFAULT_CONFIG_PER_TASK, AutoConfigurator
from otx.types import PathLike
from otx.types.device import DeviceType
from otx.types.export import OTXExportFormatType
from otx.types.precision import OTXPrecisionType
from otx.types.task import OTXTaskType
from otx.utils.device import get_available_device, is_xpu_available
from otx.utils.utils import measure_flops

if TYPE_CHECKING:
    from lightning import Callback
    from lightning.pytorch.loggers import Logger
    from lightning.pytorch.utilities.types import EVAL_DATALOADERS
    from pytorch_lightning.trainer.connectors.accelerator_connector import _PRECISION_INPUT

    from otx.data.dataset.base import OTXDataset
    from otx.metrics import MetricCallable
    from otx.types.types import DATA, MODEL


@contextmanager
def override_metric_callable(model: OTXModel, new_metric_callable: MetricCallable | None) -> Iterator[OTXModel]:
    """Override `OTXModel.metric_callable` to change the evaluation metric.

    Args:
        model: Model to override its metric callable
        new_metric_callable: If not None, override the model's one with this. Otherwise, do not override.
    """
    if new_metric_callable is None:
        yield model
        return

    orig_metric_callable = model.metric_callable
    try:
        model.metric_callable = new_metric_callable
        yield model
    finally:
        model.metric_callable = orig_metric_callable


class OTXEngine(Engine):
    """OTX Engine.

    This class defines the Engine for OTX, which governs each step of the OTX workflow.
    """

    _EXPORTED_MODEL_BASE_NAME: ClassVar[str] = "exported_model"

    def __init__(
        self,
        model: OTXModel | PathLike,
        data: OTXDataModule | PathLike,
        work_dir: PathLike = "./otx-workspace",
        checkpoint: PathLike | None = None,
        device: DeviceType = DeviceType.auto,
        num_devices: int = 1,
        **kwargs,
    ):
        """Initializes the OTX Engine.

        Args:
            model (OTXModel | PathLike): The OTX model for the engine or model config path.
            data (OTXDataModule | PathLike): The data module for the engine
                or root directory for the data.
            work_dir (PathLike, optional): Working directory for the engine. Defaults to "./otx-workspace".
            checkpoint (PathLike | None, optional): Path to the checkpoint file (model weights). Defaults to None.
            device (DeviceType, optional): The device type to use. Defaults to DeviceType.auto.
            num_devices (int, optional): The number of devices to use. If it is 2 or more, it will behave as multi-gpu.
            **kwargs: Additional keyword arguments for pl.Trainer.
        """
        self._cache = TrainerArgumentsCache(**kwargs)
        self.work_dir = work_dir
        self.device = device  # type: ignore[assignment]
        self.num_devices = num_devices
        if not isinstance(data, (OTXDataModule, str, os.PathLike)):
            msg = f"data should be OTXDataModule or PathLike, but got {type(data)}"
            raise TypeError(msg)
        self._auto_configurator = AutoConfigurator(
            data_root=data if isinstance(data, (str, os.PathLike)) else None,
            task=data.task if isinstance(data, OTXDataModule) else None,
            model_config_path=None if isinstance(model, OTXModel) else model,
        )
        self._datamodule: OTXDataModule = (
            data if isinstance(data, OTXDataModule) else self._auto_configurator.get_datamodule()
        )

        self._trainer: Trainer | None = None

        if not isinstance(model, OTXModel):
            get_model_args: dict[str, Any] = {}
            get_model_args["label_info"] = self._datamodule.label_info
            input_size = self._datamodule.input_size
            get_model_args["data_input_params"] = DataInputParams(
                input_size=input_size,
                mean=self._datamodule.input_mean,
                std=self._datamodule.input_std,
            )

            model = self._auto_configurator.get_model(**get_model_args)

        self._model: OTXModel = model
        self.task = self._model.task
        self.checkpoint = checkpoint
        if self.checkpoint:
            if not isinstance(self.checkpoint, (Path, str)) and not Path(self.checkpoint).exists():
                msg = f"Checkpoint {self.checkpoint} does not exist."
                raise FileNotFoundError(msg)
            chkpt = self._load_model_checkpoint(self.checkpoint, map_location="cpu")
            self._model.load_state_dict_incrementally(chkpt)

    # ------------------------------------------------------------------------ #
    # General OTX Entry Points
    # ------------------------------------------------------------------------ #

    def train(
        self,
        max_epochs: int | None = 200,
        min_epochs: int = 1,
        seed: int | None = None,
        deterministic: bool | Literal["warn"] = False,
        precision: _PRECISION_INPUT | None = 16,
        callbacks: list[Callback] | Callback | None = None,
        logger: Logger | Iterable[Logger] | bool | None = None,
        resume: bool = False,
        metric: MetricCallable | None = None,
        checkpoint: PathLike | None = None,
        adaptive_bs: Literal["None", "Safe", "Full"] = "None",
        check_val_every_n_epoch: int | None = 1,
        num_sanity_val_steps: int | None = 0,
        gradient_clip_val: float | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        r"""Trains the model using the provided LightningModule and OTXDataModule.

        Args:
            max_epochs (int | None, optional): The maximum number of epochs. Defaults to None.
            min_epochs (int | None, optional): The minimum number of epochs. Defaults to 1.
            seed (int | None, optional): The random seed. Defaults to None.
            deterministic (bool | Literal["warn"]): Whether to enable deterministic behavior.
                Also, can be set to `warn` to avoid failures, because some operations don't
                support deterministic mode. Defaults to False.
            precision (_PRECISION_INPUT | None, optional): The precision of the model. Defaults to 16.
            callbacks (list[Callback] | Callback | None, optional): The callbacks to be used during training.
            logger (Logger | Iterable[Logger] | bool | None, optional): The logger(s) to be used. Defaults to None.
            resume (bool, optional): If True, tries to resume training from existing checkpoint.
            metric (MetricCallable | None): If not None, it will override `OTXModel.metric_callable` with the given
                metric callable. It will temporarilly change the evaluation metric for the validation and test.
            checkpoint (PathLike | None, optional): Path to the checkpoint file. Defaults to None.
            adaptive_bs (Literal["None", "Safe", "Full"]):
                Change the actual batch size depending on the current GPU status.
                Safe => Prevent GPU out of memory. Full => Find a batch size using most of GPU memory.
                Defaults to "None".
            check_val_every_n_epoch (int | None, optional): How often to check validation. Defaults to 1.
            num_sanity_val_steps (int | None, optional): Number of validation steps to run before training starts.
            gradient_clip_val (float | None, optional): The value for gradient clipping. Defaults to None.
            **kwargs: Additional keyword arguments for pl.Trainer configuration.

        Returns:
            dict[str, Any]: A dictionary containing the callback metrics from the trainer.

        Example:
            >>> engine.train(
            ...     max_epochs=3,
            ...     seed=1234,
            ...     deterministic=False,
            ...     precision="32",
            ... )

        CLI Usage:
            1. Can pick a model or datamodule as Config file.
                ```shell
                >>> otx train \
                ...     --data_root <DATASET_PATH, str> \
                ...     --config <CONFIG, str> \
                ```
            2. Of course, can override the various values with commands.
                ```shell
                >>> otx train \
                ...     --config <CONFIG, str> \
                ...     --data_root <DATASET_PATH, str> \
                ...     --max_epochs <EPOCHS, int> \
                ...     --checkpoint <CKPT_PATH, str>
                ```
            3. To reproduce the existing training with work_dir, run
                ```shell
                >>> otx train --work_dir <WORK_DIR_PATH, str>
                ```
            4. To resume training, run
                ```shell
                >>> otx train \
                ...     --config <CONFIG, str> \
                ...     --data_root <DATASET_PATH, str> \
                ...     --checkpoint <CKPT_PATH, str>
                ...     --resume True
                ```
        """
        checkpoint = checkpoint if checkpoint is not None else self.checkpoint
        if adaptive_bs != "None":
            adapt_batch_size(engine=self, **locals(), not_increase=(adaptive_bs != "Full"))

        if seed is not None:
            seed_everything(seed, workers=True)

        self._build_trainer(
            logger=logger,
            callbacks=callbacks,
            precision=precision,
            max_epochs=max_epochs,
            min_epochs=min_epochs,
            deterministic=deterministic,
            check_val_every_n_epoch=check_val_every_n_epoch,
            num_sanity_val_steps=num_sanity_val_steps,
            gradient_clip_val=gradient_clip_val,
            **kwargs,
        )
        fit_kwargs: dict[str, Any] = {}

        # NOTE: Model's label info should be converted datamodule's label info before ckpt loading
        # This is due to smart weight loading check label name as well as number of classes.
        if self.model.label_info != self.datamodule.label_info:
            msg = (
                "Model label_info is not equal to the Datamodule label_info. "
                f"It will be overriden: {self.model.label_info} => {self.datamodule.label_info}"
            )
            logging.warning(msg)
            self.model.label_info = self.datamodule.label_info

        if resume and checkpoint:
            # NOTE: If both `resume` and `checkpoint` are provided,
            # load the entire model state from the checkpoint using the pl.Trainer's API.
            fit_kwargs["ckpt_path"] = checkpoint
        elif not resume and checkpoint:
            # NOTE: If `resume` is not enabled but `checkpoint` is provided,
            # load the model state from the checkpoint incrementally.
            # This means only the model weights are loaded. If there is a mismatch in label_info,
            # perform incremental weight loading for the model's classification layer.
            ckpt = self._load_model_checkpoint(checkpoint, map_location="cpu")
            self.model.load_state_dict_incrementally(ckpt)

        with override_metric_callable(model=self.model, new_metric_callable=metric) as model:
            # Setup DataAugSwitch for datasets before training starts
            self._setup_data_aug_switch_for_datasets()

            self.trainer.fit(
                model=model,
                datamodule=self.datamodule,
                **fit_kwargs,
            )
        self.checkpoint = self.trainer.checkpoint_callback.best_model_path

        if not isinstance(self.checkpoint, (Path, str)):
            msg = "self.checkpoint should be Path or str at this time."
            raise TypeError(msg)

        best_checkpoint_symlink = Path(self.work_dir) / "best_checkpoint.ckpt"
        if best_checkpoint_symlink.is_symlink():
            best_checkpoint_symlink.unlink()
        best_checkpoint_symlink.symlink_to(self.checkpoint)

        return self.trainer.callback_metrics

    def test(
        self,
        checkpoint: PathLike | None = None,
        datamodule: EVAL_DATALOADERS | OTXDataModule | None = None,
        metric: MetricCallable | None = None,
        **kwargs,
    ) -> dict:
        r"""Run the testing phase of the engine.

        Args:
            checkpoint (PathLike | None, optional): Path to the checkpoint file to load the model from.
                Defaults to None.
            datamodule (EVAL_DATALOADERS | OTXDataModule | None, optional): The data module containing the test data.
            metric (MetricCallable | None): If not None, it will override `OTXModel.metric_callable` with the given
                metric callable. It will temporarilly change the evaluation metric for the validation and test.
            **kwargs: Additional keyword arguments for pl.Trainer configuration.

        Returns:
            dict: Dictionary containing the callback metrics from the trainer.

        Example:
            >>> engine.test(
            ...     datamodule=OTXDataModule(),
            ...     checkpoint=<checkpoint/path>,
            ... )

        CLI Usage:
            1. To eval model by specifying the work_dir where did the training, run
                ```shell
                >>> otx test --work_dir <WORK_DIR_PATH, str>
                ```
            2. To eval model a specific checkpoint, run
                ```shell
                >>> otx test --work_dir <WORK_DIR_PATH, str> --checkpoint <CKPT_PATH, str>
                ```
            3. Can pick a model.
                ```shell
                >>> otx test \
                ...     --config <CONFIG | CLASS_PATH_OR_NAME> \
                ...     --data_root <DATASET_PATH, str> \
                ...     --checkpoint <CKPT_PATH, str>
                ```
        """
        model = self.model
        checkpoint = checkpoint if checkpoint is not None else self.checkpoint
        datamodule = datamodule if datamodule is not None else self.datamodule

        if Path(str(checkpoint)).suffix in [".xml", ".onnx"]:
            msg = "OTXEngine doesn't support validation of exported models. Please, use OVEnging instead."

        # NOTE, trainer.test takes only lightning based checkpoint.
        # So, it can't take the OTX1.x checkpoint.
        if checkpoint is not None:
            ckpt = self._load_model_checkpoint(checkpoint, map_location="cpu")
            model.load_state_dict(ckpt)

        if model.label_info != self.datamodule.label_info:
            if (
                self.task == "SEMANTIC_SEGMENTATION"
                and "otx_background_lbl" in self.datamodule.label_info.label_names
                and (len(self.datamodule.label_info.label_names) - len(model.label_info.label_names) == 1)
            ):
                # workaround for background label
                model.label_info = copy.deepcopy(self.datamodule.label_info)
            else:
                msg = (
                    "To launch a test pipeline, the label information should be same "
                    "between the training and testing datasets. "
                    "Please check whether you use the same dataset: "
                    f"model.label_info={model.label_info}, "
                    f"datamodule.label_info={self.datamodule.label_info}"
                )
                raise ValueError(msg)

        self._build_trainer(**kwargs)

        with override_metric_callable(model=model, new_metric_callable=metric) as model:
            self.trainer.test(
                model=model,
                dataloaders=datamodule,
            )

        return self.trainer.callback_metrics

    def predict(
        self,
        checkpoint: PathLike | None = None,
        datamodule: EVAL_DATALOADERS | OTXDataModule | None = None,
        explain: bool = False,
        explain_config: ExplainConfig | None = None,
        **kwargs,
    ) -> list:
        r"""Run predictions using the specified model and data.

        Args:
            checkpoint (PathLike | None, optional): The path to the checkpoint file to load the model from.
            datamodule (EVAL_DATALOADERS | OTXDataModule | None, optional): The data module to use for predictions.
            explain (bool, optional): Whether to dump "saliency_map" and "feature_vector" or not.
            explain_config (ExplainConfig | None, optional): Explain configuration used for saliency map post-processing
            **kwargs: Additional keyword arguments for pl.Trainer configuration.

        Returns:
            list | None: The predictions if `return_predictions` is True, otherwise None.

        Example:
            >>> engine.predict(
            ...     datamodule=OTXDataModule(),
            ...     checkpoint=<checkpoint/path>,
            ...     return_predictions=True,
            ...     explain=True,
            ... )

        CLI Usage:
            1. To predict a model with work_dir, run
                ```shell
                >>> otx predict --work_dir <WORK_DIR_PATH, str>
                ```
            2. To predict a specific model, run
                ```shell
                >>> otx predict \
                ...     --work_dir <WORK_DIR_PATH, str> \
                ...     --checkpoint <CKPT_PATH, str>
                ```
            3. To predict with configuration file, run
                ```shell
                >>> otx predict \
                ...     --config <CONFIG_PATH, str> \
                ...     --checkpoint <CKPT_PATH, str>
                ```
        """
        from otx.backend.native.models.utils.xai_utils import process_saliency_maps_in_pred_entity

        model = self.model

        checkpoint = checkpoint if checkpoint is not None else self.checkpoint
        datamodule = datamodule if datamodule is not None else self.datamodule

        if checkpoint is not None:
            ckpt = self._load_model_checkpoint(checkpoint, map_location="cpu")
            model.load_state_dict(ckpt)

        if model.label_info != self.datamodule.label_info:
            msg = (
                "To launch a predict pipeline, the label information should be same "
                "between the training and testing datasets. "
                "Please check whether you use the same dataset: "
                f"model.label_info={model.label_info}, "
                f"datamodule.label_info={self.datamodule.label_info}"
            )
            raise ValueError(msg)

        self._build_trainer(**kwargs)

        curr_explain_mode = model.explain_mode

        try:
            model.explain_mode = explain
            predict_result = self.trainer.predict(
                model=model,
                dataloaders=datamodule,
                return_predictions=True,
            )
        finally:
            model.explain_mode = curr_explain_mode

        if explain:
            if explain_config is None:
                explain_config = ExplainConfig()

            predict_result = process_saliency_maps_in_pred_entity(predict_result, explain_config, datamodule.label_info)

        return predict_result

    def export(
        self,
        checkpoint: PathLike | None = None,
        export_format: OTXExportFormatType = OTXExportFormatType.OPENVINO,
        export_precision: OTXPrecisionType = OTXPrecisionType.FP32,
        explain: bool = False,
        export_demo_package: bool = False,
        **kwargs,
    ) -> Path:
        r"""Export the trained model to OpenVINO Intermediate Representation (IR) or ONNX formats.

        Args:
            checkpoint (PathLike | None, optional): Checkpoint to export. Defaults to None.
            export_config (ExportConfig | None, optional): Config that allows to set export
            format and precision. Defaults to None.
            explain (bool): Whether to get "saliency_map" and "feature_vector" or not.
            export_demo_package (bool): Whether to export demo package with the model.
                Only OpenVINO model can be exported with demo package.

        Returns:
            Path: Path to the exported model.

        Example:
            >>> engine.export(
            ...     checkpoint=<checkpoint/path>,
            ...     export_format=OTXExportFormatType.OPENVINO,
            ...     export_precision=OTXExportPrecisionType.FP32,
            ...     explain=True,
            ... )

        CLI Usage:
            1. To export a model with default setting (OPENVINO, FP32), run
                ```shell
                >>> otx export --work_dir <WORK_DIR_PATH, str>
                ```
            2. To export a specific checkpoint, run
                ```shell
                >>> otx export \
                    --config <CONFIG_PATH, str> --checkpoint <CKPT_PATH, str> \
                    --data_root <DATASET_PATH, str>
                ```
            3. To export a model with precision FP16 and format ONNX, run
                ```shell
                >>> otx export ... \
                ...     --export_precision FP16 --export_format ONNX
                ```
            4. To export model with 'saliency_map' and 'feature_vector', run
                ```shell
                >>> otx export ... \
                ...     --explain True
                ```
        """
        checkpoint = checkpoint if checkpoint is not None else self.checkpoint

        if checkpoint is None:
            msg = "To make export, checkpoint must be specified."
            raise RuntimeError(msg)
        if export_demo_package and export_format == OTXExportFormatType.ONNX:
            msg = (
                "ONNX export is not supported in exportable code mode. Exportable code parameter will be disregarded. "
            )
            warn(msg, stacklevel=1)
            export_demo_package = False

        ckpt = self._load_model_checkpoint(checkpoint, map_location="cpu")
        self.model.load_state_dict(ckpt)
        self.model.eval()

        self.model.explain_mode = explain
        exported_model_path = self.model.export(
            output_dir=Path(self.work_dir),
            base_name=self._EXPORTED_MODEL_BASE_NAME,
            export_format=export_format,
            precision=export_precision,
            to_exportable_code=export_demo_package,
        )

        self.model.explain_mode = False
        return exported_model_path

    def benchmark(
        self,
        checkpoint: PathLike | None = None,
        batch_size: int = 1,
        n_iters: int = 10,
        extended_stats: bool = False,
        print_table: bool = True,
    ) -> dict[str, str]:
        r"""Executes model micro benchmarking on random data.

        Benchmark can provide latency, throughput, number of parameters,
        and theoretical computational complexity with batch size 1.
        The latter two characteristics are available for torch model recipes only.
        Before the measurements, a warm-up is done.

        Args:
            checkpoint (PathLike | None, optional): Path to checkpoint. Optional for torch models. Defaults to None.
            batch_size (int, optional): Batch size for benchmarking. Defaults to 1.
            n_iters (int, optional): Number of iterations to average on. Defaults to 10.
            extended_stats (bool, optional): Flag that enables printing of per module complexity for torch model.
                Defaults to False.
            print_table (bool, optional): Flag that enables printing the benchmark results in a rich table.
                Defaults to True.

        Returns:
            dict[str, str]: a dict with the benchmark results.

        Example:
            >>> engine.benchmark(
            ...     checkpoint=<checkpoint-path>,
            ...     batch_size=1,
            ...     n_iters=20,
            ...     extended_stats=True,
            ... )

        CLI Usage:
            1. To run benchmark by specifying the work_dir where did the training, run
                ```shell
                >>> otx benchmark --work_dir <WORK_DIR_PATH, str>
                ```
            2. To run benchmark by specifying the checkpoint, run
                ```shell
                >>> otx benchmark \
                ...     --work_dir <WORK_DIR_PATH, str> \
                ...     --checkpoint <CKPT_PATH, str>
                ```
            3. To run benchmark using the configuration, launch
                ```shell
                >>> otx benchmark \
                ...     --config <CONFIG_PATH> \
                ...     --data_root <DATASET_PATH, str> \
                ...     --checkpoint <CKPT_PATH, str>
                ```
        """
        checkpoint = checkpoint if checkpoint is not None else self.checkpoint

        if checkpoint is not None:
            ckpt = self._load_model_checkpoint(checkpoint, map_location="cpu")
            self.model.load_state_dict(ckpt)
        self.model.eval()

        def dummy_infer(model: OTXModel, batch_size: int = 1) -> float:
            input_batch = model.get_dummy_input(batch_size)
            start = time.perf_counter()
            model.forward(input_batch)
            end = time.perf_counter()
            return end - start

        warmup_iters = max(1, int(n_iters / 10))
        for _ in range(warmup_iters):
            dummy_infer(self.model, batch_size)

        total_time = 0.0
        for _ in range(n_iters):
            total_time += dummy_infer(self.model, batch_size)
        latency = total_time / n_iters
        fps = batch_size / latency

        final_stats = {"latency": f"{latency:.3f} s", "throughput": f"{(fps):.3f} FPS"}

        try:
            from torch.utils.flop_counter import convert_num_with_suffix, get_suffix_str

            input_batch = self.model.get_dummy_input(1)
            model_fwd = lambda: self.model.forward(input_batch)
            depth = 3 if extended_stats else 0
            fwd_flops = measure_flops(model_fwd, print_stats_depth=depth)
            flops_str = convert_num_with_suffix(fwd_flops, get_suffix_str(fwd_flops * 10**3))
            final_stats["complexity"] = flops_str + " MACs"
        except Exception as e:
            logging.warning(f"Failed to complete complexity estimation: {e}")

            params_num = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
            params_num_str = convert_num_with_suffix(params_num, get_suffix_str(params_num * 100))
            final_stats["parameters_number"] = params_num_str

        if print_table:
            from rich.console import Console
            from rich.table import Column, Table

            console = Console()
            table_headers = ["Benchmark", "Value"]
            columns = [Column(h, justify="center", style="magenta", width=console.width) for h in table_headers]
            columns[0].style = "cyan"
            table = Table(*columns)
            for name, val in final_stats.items():
                table.add_row(*[f"{name:<20}", f"{val}"])
            console.print(table)

        with (Path(self.work_dir) / "benchmark_report.csv").open("w") as f:
            writer = csv.writer(f)
            writer.writerow(list(final_stats))
            writer.writerow(list(final_stats.values()))

        return final_stats

    @classmethod
    def from_config(
        cls,
        config_path: PathLike,
        data_root: PathLike | None = None,
        work_dir: PathLike | None = None,
        **kwargs,
    ) -> OTXEngine:
        """Builds the engine from a configuration file.

        Args:
            config_path (PathLike): The configuration file path.
            data_root (PathLike | None): Root directory for the data.
                Defaults to None. If data_root is None, use the data_root from the configuration file.
            work_dir (PathLike | None, optional): Working directory for the engine.
                Defaults to None. If work_dir is None, use the work_dir from the configuration file.
            kwargs: Arguments that can override the engine's arguments.

        Returns:
            Engine: An instance of the Engine class.

        Example:
            >>> engine = OTXEngine.from_config(
            ...     config="config.yaml",
            ... )
            ... engine.train()
        """
        from otx.cli.utils.jsonargparse import get_instantiated_classes

        # For the Engine argument, prepend 'engine.' for CLI parser
        filter_kwargs = ["device", "checkpoint", "task"]
        for key in filter_kwargs:
            if key in kwargs:
                kwargs[f"engine.{key}"] = kwargs.pop(key)
        instantiated_config, train_kwargs = get_instantiated_classes(
            config=config_path,
            data_root=data_root,
            work_dir=work_dir,
            **kwargs,
        )
        engine_kwargs = {**instantiated_config.get("engine", {}), **train_kwargs}

        # Remove any input that is not currently available in Engine and print a warning message.
        set_valid_args = TrainerArgumentsCache.get_trainer_constructor_args().union(
            set(inspect.signature(OTXEngine.__init__).parameters.keys()),
        )
        removed_args = []
        for engine_key in list(engine_kwargs.keys()):
            if engine_key not in set_valid_args:
                engine_kwargs.pop(engine_key)
                removed_args.append(engine_key)
        if removed_args:
            msg = (
                f"Warning: {removed_args} -> not available in Engine constructor. "
                "It will be ignored. Use what need in the right places."
            )
            warn(msg, stacklevel=1)

        if (datamodule := instantiated_config.get("data")) is None:
            msg = "Cannot instantiate datamodule from config."
            raise ValueError(msg)
        if not isinstance(datamodule, OTXDataModule):
            raise TypeError(datamodule)

        if (model := instantiated_config.get("model")) is None:
            msg = "Cannot instantiate model from config."
            raise ValueError(msg)
        if not isinstance(model, OTXModel):
            raise TypeError(model)

        model.label_info = datamodule.label_info

        return cls(
            work_dir=instantiated_config.get("work_dir", work_dir),
            data=datamodule,
            model=model,
            **engine_kwargs,
        )

    @classmethod
    def from_model_name(
        cls,
        model_name: str,
        task: OTXTaskType,
        data_root: PathLike | None = None,
        work_dir: PathLike | None = None,
        **kwargs,
    ) -> OTXEngine:
        """Builds the engine from a model name.

        Args:
            model_name (str): The model name.
            task (OTXTaskType): The type of OTX task.
            data_root (PathLike | None): Root directory for the data.
                Defaults to None. If data_root is None, use the data_root from the configuration file.
            work_dir (PathLike | None, optional): Working directory for the engine.
                Defaults to None. If work_dir is None, use the work_dir from the configuration file.
            kwargs: Arguments that can override the engine's arguments.

        Returns:
            OTXEngine: An instance of the OTXEngine class.

        Example:
            >>> engine = OTXEngine.from_model_name(
            ...     model_name="atss_mobilenetv2",
            ...     task="DETECTION",
            ...     data_root=<dataset/path>,
            ... )
            ... engine.train()

            If you want to override configuration from default config:
                >>> overriding = {
                ...     "data.train_subset.batch_size": 2,
                ...     "data.test_subset.subset_name": "TESTING",
                ... }
                >>> engine = OTXEngine(
                ...     model_name="atss_mobilenetv2",
                ...     task="DETECTION",
                ...     data_root=<dataset/path>,
                ...     **overriding,
                ... )
        """
        default_config = DEFAULT_CONFIG_PER_TASK.get(task)
        model_path = str(default_config).split("/")
        model_path[-1] = f"{model_name}.yaml"
        config = Path("/".join(model_path))
        if not config.exists():
            candidate_list = [model.stem for model in config.parent.glob("*")]
            msg = (
                f"Model config file not found: {config}, please check the model name. "
                f"Available models for {task} task are {candidate_list}"
            )
            raise FileNotFoundError(msg)

        return cls.from_config(
            config_path=config,
            data_root=data_root,
            work_dir=work_dir,
            **kwargs,
        )

    # ------------------------------------------------------------------------ #
    # Property and setter functions provided by Engine.
    # ------------------------------------------------------------------------ #

    @property
    def work_dir(self) -> PathLike:
        """Work directory."""
        return self._work_dir

    @work_dir.setter
    def work_dir(self, work_dir: PathLike) -> None:
        self._work_dir = work_dir
        self._cache.update(default_root_dir=work_dir)
        self._cache.is_trainer_args_identical = False

    @property
    def device(self) -> DeviceConfig:
        """Device engine uses."""
        return self._device

    @device.setter
    def device(self, device: DeviceType) -> None:
        if is_xpu_available() and device == DeviceType.auto:
            device = DeviceType.xpu
        self._device = DeviceConfig(accelerator=device)
        self._cache.update(accelerator=self._device.accelerator, devices=self._device.devices)
        self._cache.is_trainer_args_identical = False

    @property
    def num_devices(self) -> int:
        """Number of devices for Engine use."""
        return self._device.devices

    @num_devices.setter
    def num_devices(self, num_devices: int) -> None:
        """Setter function for multi-gpu."""
        self._device.devices = num_devices
        self._cache.update(devices=self._device.devices)
        self._cache.is_trainer_args_identical = False

    @property
    def trainer(self) -> Trainer:
        """Returns the trainer object associated with the engine.

        To get this property, you should execute `OTXEngine.train()` function first.

        Returns:
            Trainer: The trainer object.
        """
        if self._trainer is None:
            msg = "Please run train() first"
            raise RuntimeError(msg)
        return self._trainer

    def _build_trainer(self, logger: Logger | Iterable[Logger] | bool | None = None, **kwargs) -> None:
        """Instantiate the trainer based on the model parameters."""
        if self._cache.requires_update(**kwargs) or self._trainer is None:
            self._apply_param_overrides(kwargs)
            # set up xpu device
            self.configure_accelerator()
            # setup default loggers
            logger = self.configure_loggers(logger)
            # set up default callbacks
            self.configure_callbacks()

            kwargs = self._cache.args
            self._trainer = Trainer(logger=logger, **kwargs)
            self._cache.is_trainer_args_identical = True
            self._trainer.task = self.task
            self.work_dir = self._trainer.default_root_dir

    def _apply_param_overrides(self, param_kwargs: dict[str, Any]) -> None:
        """Apply parameter overrides based on the current local variables."""
        sig = inspect.signature(self.train)
        add_kwargs = param_kwargs.pop("kwargs", {})
        for param_name, param in sig.parameters.items():
            if param_name in param_kwargs and param_name in self._cache.args:
                # if both `param_kwargs` and `_cache.args` have the same parameter,
                # we will use the value from `param_kwargs` if it is different from the default
                # value of the parameter.
                # Otherwise, we will keep the value from `_cache.args`.
                current_value = param_kwargs.pop(param_name)
                if current_value != param.default:
                    self._cache.args[param_name] = current_value
        # update the cache with the remaining parameters
        self._cache.update(**param_kwargs)
        self._cache.update(**add_kwargs)

    def configure_accelerator(self) -> None:
        """Updates the cache arguments based on the device type."""
        if self._device.accelerator == DeviceType.xpu:
            self._cache.update(strategy="xpu_single")
            # add plugin for Automatic Mixed Precision on XPU
            if self._cache.args.get("precision", 32) == 16:
                self._cache.update(
                    plugins=[
                        MixedPrecision(
                            precision="bf16-mixed",
                            device="xpu",
                        ),
                    ],
                )
                self._cache.args["precision"] = None
        elif (self._device.accelerator == DeviceType.cpu) or (get_available_device() == "cpu"):
            self._cache.args["precision"] = "32"

    def configure_loggers(self, logger: Logger | Iterable[Logger] | bool | None = None) -> Logger | Iterable[Logger]:
        """Sets up the loggers for the trainer.

        If no logger is provided, it will use the default loggers.
        """
        if logger is None:
            logger = [
                CSVLogger(save_dir=self.work_dir, name="csv/", prefix=""),
                TensorBoardLogger(
                    save_dir=self.work_dir,
                    name="tensorboard/",
                    log_graph=False,
                    default_hp_metric=True,
                    prefix="",
                ),
            ]
        return logger

    def configure_callbacks(self) -> None:
        """Sets up the OTX callbacks for the trainer."""
        callbacks: list[Callback] = []
        config_callbacks = self._cache.args.get("callbacks", [])
        if config_callbacks is None:
            return
        has_callback: Callable[[Callback], bool] = lambda callback: any(
            isinstance(c, callback) for c in config_callbacks
        )

        if not has_callback(RichProgressBar):
            callbacks.append(RichProgressBar(refresh_rate=1, leave=False))
        if not has_callback(RichModelSummary):
            callbacks.append(RichModelSummary(max_depth=1))
        if not has_callback(IterationTimer):
            callbacks.append(IterationTimer(prog_bar=True, on_step=False, on_epoch=True))
        if not has_callback(LearningRateMonitor):
            callbacks.append(LearningRateMonitor(logging_interval="epoch", log_momentum=True))
        if not has_callback(ModelCheckpoint):
            callbacks.append(
                ModelCheckpoint(
                    dirpath=self.work_dir,
                    save_top_k=1,
                    save_last=True,
                    filename="checkpoints/epoch_{epoch:03d}",
                    auto_insert_metric_name=False,
                ),
            )
        if not has_callback(AdaptiveTrainScheduling):
            callbacks.append(
                AdaptiveTrainScheduling(
                    max_interval=5,
                    decay=-0.025,
                    min_earlystop_patience=5,
                    min_lrschedule_patience=3,
                ),
            )
        if not has_callback(GPUMemMonitor):
            callbacks.append(GPUMemMonitor())

        self._cache.args["callbacks"] = callbacks + config_callbacks

        # Setup DataAugSwitch with shared multiprocessing.Value
        self._setup_augmentation_scheduler()

    def _setup_augmentation_scheduler(self) -> None:
        """Set up shared memory for DataAugSwitch and AugmentationSchedulerCallback.

        Why is this handled here in the engine?
        -------------------------------------------------
        Data augmentation scheduling is a cross-cutting concern that affects both the data pipeline
        (datasets, dataloaders) and the training control flow (callbacks, epoch tracking). In
        distributed or multi-process training (e.g., DDP, multi-worker dataloaders), each process or
        worker may have its own copy of the dataset and augmentation logic. If the augmentation policy
        (e.g., which transforms to apply at a given epoch) is not synchronized across all processes,
        different workers may apply different augmentations for the same epoch, leading to
        non-deterministic, irreproducible, or even incorrect training.

        The engine is the only component with global visibility and control over:
          - The full set of callbacks (including augmentation scheduling callbacks)
          - The configuration and instantiation of datasets and dataloaders
          - The orchestration of training, including distributed/multiprocessing setup

        By handling augmentation scheduler setup here, we ensure:
          - The current epoch (which determines augmentation policy) is stored in a shared
            multiprocessing.Value, so all processes and workers see the same value.
          - The DataAugSwitch instance used by the callback and (optionally) by datasets
            is referencing the same shared epoch state.
          - This setup is performed before training starts, so all components are properly
            synchronized from the beginning.

        Without this centralized setup, it would be easy for different parts of the system
        to become unsynchronized, leading to subtle bugs that are hard to debug and reproduce.
        By making the engine responsible for this, we guarantee correct, deterministic, and
        reproducible augmentation scheduling across all training processes.

        Implementation:
        ----------------
        This method locates the AugmentationSchedulerCallback among the configured callbacks,
        and if it has a DataAugSwitch instance, it creates a shared integer value for the
        epoch and assigns it to the DataAugSwitch. This must be done before training starts.

        """
        aug_scheduler_callback = None

        # Find AugmentationSchedulerCallback in all callbacks
        all_callbacks = self._cache.args.get("callbacks", [])
        for callback in all_callbacks:
            if isinstance(callback, AugmentationSchedulerCallback):
                aug_scheduler_callback = callback
                break

        # If AugmentationSchedulerCallback exists and has a data_aug_switch, set up shared memory
        if aug_scheduler_callback is not None and aug_scheduler_callback.data_aug_switch is not None:
            # Create shared multiprocessing.Value for epoch tracking
            shared_epoch = Value("i", 0)
            aug_scheduler_callback.data_aug_switch.set_shared_epoch(shared_epoch)

    def _setup_data_aug_switch_for_datasets(self) -> None:
        """Set up DataAugSwitch for datasets before training starts, ensuring shared memory for augmentation policy.

        By assigning the same DataAugSwitch instance (with its shared epoch value) to the training dataset(s),
        we guarantee that all data loading workers and processes reference the same epoch state. This prevents
        inconsistencies where different processes might otherwise apply different augmentation policies due to
        unsynchronized epoch tracking. Without this setup, augmentation switching could become non-deterministic
        or incorrect, leading to irreproducible results or degraded training performance.

        This method locates the AugmentationSchedulerCallback and its DataAugSwitch, then attaches the switch
        to any dataset that supports dynamic augmentation switching (i.e., implements DataAugSwitchMixin).
        """
        if self._trainer is None:
            return

        # Find AugmentationSchedulerCallback and its DataAugSwitch
        data_aug_switch = None
        for callback in self._trainer.callbacks:
            if isinstance(callback, AugmentationSchedulerCallback) and callback.data_aug_switch is not None:
                data_aug_switch = callback.data_aug_switch
                break

        if data_aug_switch is None:
            msg = "DataAugSwitch not found in AugmentationSchedulerCallback"
            logging.warning(msg)
            return

        def set_data_aug_switch_if_supported(dataset: OTXDataset) -> bool:
            """Set data_aug_switch on a dataset if it supports it."""
            from otx.data.dataset.mixins import DataAugSwitchMixin

            if isinstance(dataset, DataAugSwitchMixin):
                dataset.set_data_aug_switch(data_aug_switch)
                return True
            return False

        # Set DataAugSwitch for the training dataset
        if (
            hasattr(self.datamodule, "subsets")
            and "train" in self.datamodule.subsets
            and set_data_aug_switch_if_supported(self.datamodule.subsets["train"])
        ):
            msg = "DataAugSwitch set for train_dataset"
            logging.info(msg)

    @property
    def trainer_params(self) -> dict:
        """Returns the parameters used for training the model.

        Returns:
            dict: A dictionary containing the training parameters.
        """
        return self._cache.args

    @property
    def model(self) -> OTXModel:
        """Returns the model object associated with the engine.

        Returns:
            OTXModel: The OTXModel object.
        """
        return self._model

    @property
    def datamodule(self) -> OTXDataModule:
        """Returns the datamodule object associated with the engine.

        Returns:
            OTXDataModule: The OTXDataModule object.
        """
        if self._datamodule is None:
            msg = "Please include the `data_root` or `datamodule` when creating the Engine."
            raise RuntimeError(msg)
        return self._datamodule

    @staticmethod
    def is_supported(model: MODEL, data: DATA) -> bool:
        """Check if the engine is supported for the given model and data."""
        return bool(isinstance(model, OTXModel) and isinstance(data, OTXDataModule))

    @staticmethod
    def _load_model_checkpoint(checkpoint: PathLike, map_location: str | None = None) -> dict[str, Any]:
        """Load model checkpoint from the given path.

        Args:
            checkpoint (PathLike): Path to the checkpoint file.

        Returns:
            dict[str, Any]: The loaded state dictionary from the checkpoint.
        """
        if not Path(checkpoint).exists():
            msg = f"Checkpoint file does not exist: {checkpoint}"
            raise FileNotFoundError(msg)

        try:
            ckpt = torch.load(checkpoint, map_location=map_location)
        except UnpicklingError:
            from otx.backend.native.utils.utils import mock_modules_for_chkpt

            with mock_modules_for_chkpt():
                ckpt = torch.load(checkpoint, map_location=map_location, weights_only=False)
        except Exception as e:
            msg = f"Failed to load checkpoint from {checkpoint}. Please check the file."
            raise RuntimeError(e) from None

        return ckpt
