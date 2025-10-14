# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""LightningDataModule extension for OTX."""

from __future__ import annotations

import logging as log
from typing import TYPE_CHECKING

from datumaro import Dataset as DmDataset
from lightning import LightningDataModule
from omegaconf import DictConfig, OmegaConf
from torch.utils.data import DataLoader, RandomSampler
from torchvision.transforms.v2 import Normalize

from otx.config.data import TileConfig
from otx.data.dataset.tile import OTXTileDatasetFactory
from otx.data.factory import OTXDatasetFactory
from otx.data.utils import adapt_input_size_to_dataset, adapt_tile_config, get_adaptive_num_workers, instantiate_sampler
from otx.data.utils.pre_filtering import pre_filtering
from otx.types.device import DeviceType
from otx.types.image import ImageColorChannel
from otx.types.label import LabelInfo
from otx.types.task import OTXTaskType

if TYPE_CHECKING:
    from lightning.pytorch.utilities.parsing import AttributeDict

    from otx.config.data import SubsetConfig
    from otx.data.dataset.base import OTXDataset


class OTXDataModule(LightningDataModule):
    """This class extends the LightningDataModule to provide data handling capabilities for the OTX pipeline.

    Args:
        task (OTXTaskType): The type of task (e.g., classification, detection).
        data_format (str): The format of the data (e.g., 'coco', 'voc').
        data_root (str): The root directory where the data is stored.
        train_subset (SubsetConfig): Configuration for the training subset.
        val_subset (SubsetConfig): Configuration for the validation subset.
        test_subset (SubsetConfig): Configuration for the test subset.
        tile_config (TileConfig, optional): Configuration for tiling.
        Defaults to TileConfig(enable_tiler=False).
        image_color_channel (ImageColorChannel, optional): Color channel configuration for images.
        Defaults to ImageColorChannel.RGB.
        include_polygons (bool, optional): Whether to include polygons in the data. Defaults to False.
        ignore_index (int, optional): Index to ignore in segmentation tasks. Defaults to 255.
        unannotated_items_ratio (float, optional): Ratio of unannotated items to include. Defaults to 0.0.
        auto_num_workers (bool, optional): Whether to automatically determine the number of workers. Defaults to False.
        device (DeviceType, optional): Device type to use (e.g., 'cpu', 'gpu'). Defaults to DeviceType.auto.
        input_size (tuple[int, int] | str, optional): Final image or video shape after transformation.
        Can be "auto" to determine size automatically. Defaults to "auto".
        input_size_multiplier (int, optional): Multiplier for adaptive input size.
        Useful for models requiring specific input size multiples. Defaults to 1.
    """

    def __init__(
        self,
        task: OTXTaskType,
        data_format: str,
        data_root: str,
        train_subset: SubsetConfig,
        val_subset: SubsetConfig,
        test_subset: SubsetConfig,
        tile_config: TileConfig = TileConfig(enable_tiler=False),
        image_color_channel: ImageColorChannel = ImageColorChannel.RGB,
        include_polygons: bool = False,
        ignore_index: int = 255,
        unannotated_items_ratio: float = 0.0,
        auto_num_workers: bool = False,
        device: DeviceType = DeviceType.auto,
        input_size: tuple[int, int] | str = "auto",
        input_size_multiplier: int = 1,
    ) -> None:
        """Constructor."""
        super().__init__()
        self.task = task
        self.data_format = data_format
        self.data_root = data_root

        self.train_subset = train_subset
        self.val_subset = val_subset
        self.test_subset = test_subset

        self.tile_config = tile_config

        self.image_color_channel = image_color_channel
        self.include_polygons = include_polygons
        self.ignore_index = ignore_index
        self.unannotated_items_ratio = unannotated_items_ratio

        self.auto_num_workers = auto_num_workers
        self.device = device

        self.subsets: dict[str, OTXDataset] = {}
        self.save_hyperparameters(ignore=["input_size"])

        dataset = DmDataset.import_from(self.data_root, format=self.data_format)
        if self.task != OTXTaskType.H_LABEL_CLS:
            dataset = pre_filtering(
                dataset,
                self.data_format,
                self.unannotated_items_ratio,
                self.task,
                ignore_index=self.ignore_index if self.task == "SEMANTIC_SEGMENTATION" else None,
            )
        if isinstance(input_size, str) and input_size == "auto":
            input_size = adapt_input_size_to_dataset(
                dataset,
                self.task,
                input_size_multiplier,
            )
        elif not isinstance(input_size, (tuple, list)):
            msg = f"input_size should be tuple/list of ints or 'auto', but got {input_size}"
            raise ValueError(msg)

        for subset_cfg in [train_subset, val_subset, test_subset]:
            if subset_cfg.input_size is None:
                subset_cfg.input_size = input_size  # type: ignore[assignment]

        # get mean and std from Normalize transform
        mean = (0.0, 0.0, 0.0)
        std = (1.0, 1.0, 1.0)
        if train_subset.transforms is not None:
            for transform in train_subset.transforms:
                if isinstance(transform, dict) and "Normalize" in transform.get("class_path", ""):
                    # CLI case with jsonargparse
                    mean = transform["init_args"].get("mean", (0.0, 0.0, 0.0))
                    std = transform["init_args"].get("std", (1.0, 1.0, 1.0))
                    break

                if isinstance(transform, Normalize):
                    # torchvision.transforms case
                    mean = transform.mean
                    std = transform.std
                    break

        self.input_mean = mean
        self.input_std = std
        self.input_size = input_size

        if self.tile_config.enable_tiler and self.tile_config.enable_adaptive_tiling:
            adapt_tile_config(self.tile_config, dataset=dataset, task=self.task)

        config_mapping = {
            self.train_subset.subset_name: self.train_subset,
            self.val_subset.subset_name: self.val_subset,
            self.test_subset.subset_name: self.test_subset,
        }

        if self.auto_num_workers:
            if self.device not in [DeviceType.gpu, DeviceType.auto]:
                log.warning(
                    "Only GPU device type support auto_num_workers. "
                    f"Current deveice type is {self.device!s}. auto_num_workers is skipped.",
                )
            elif (num_workers := get_adaptive_num_workers()) is not None:
                for subset_name, subset_config in config_mapping.items():
                    log.info(
                        f"num_workers of {subset_name} subset is changed : "
                        f"{subset_config.num_workers} -> {num_workers}",
                    )
                    subset_config.num_workers = num_workers

        label_infos: list[LabelInfo] = []

        for name, dm_subset in dataset.subsets().items():
            if name not in config_mapping:
                log.warning(f"{name} is not available. Skip it")
                continue

            dataset = OTXDatasetFactory.create(
                task=self.task,
                dm_subset=dm_subset.as_dataset(),
                cfg_subset=config_mapping[name],
                data_format=self.data_format,
                image_color_channel=image_color_channel,
                include_polygons=include_polygons,
                ignore_index=ignore_index,
            )

            if self.tile_config.enable_tiler:
                dataset = OTXTileDatasetFactory.create(
                    task=self.task,
                    dataset=dataset,
                    tile_config=self.tile_config,
                )
            self.subsets[name] = dataset
            label_infos += [self.subsets[name].label_info]
            log.info(f"Add name: {name}, self.subsets: {self.subsets}")

        if self._is_meta_info_valid(label_infos) is False:
            msg = "All data meta infos of subsets should be the same."
            raise ValueError(msg)

        self.label_info = next(iter(label_infos))

    def _is_meta_info_valid(self, label_infos: list[LabelInfo]) -> bool:
        """Check whether there are mismatches in the metainfo for the all subsets."""
        return bool(all(label_info == label_infos[0] for label_info in label_infos))

    def _get_dataset(self, subset: str) -> OTXDataset:
        if (dataset := self.subsets.get(subset)) is None:
            msg = f"Dataset has no '{subset}'. Available subsets = {list(self.subsets.keys())}"
            raise KeyError(msg)
        return dataset

    def train_dataloader(self) -> DataLoader:
        """Get train dataloader."""
        config = self.train_subset
        dataset = self._get_dataset(config.subset_name)
        sampler = instantiate_sampler(config.sampler, dataset=dataset, batch_size=config.batch_size)

        common_args = {
            "dataset": dataset,
            "batch_size": config.batch_size,
            "num_workers": config.num_workers,
            "pin_memory": True,
            "collate_fn": dataset.collate_fn,
            "persistent_workers": config.num_workers > 0,
            "sampler": sampler,
            "shuffle": sampler is None,
        }

        tile_config = self.tile_config
        if tile_config.enable_tiler and tile_config.sampling_ratio < 1:
            num_samples = max(1, int(len(dataset) * tile_config.sampling_ratio))
            log.info(f"Using tiled sampling with {num_samples} samples")
            common_args.update(
                {
                    "shuffle": False,
                    "sampler": RandomSampler(dataset, num_samples=num_samples),
                },
            )
        return DataLoader(**common_args)

    def val_dataloader(self) -> DataLoader:
        """Get val dataloader."""
        config = self.val_subset
        dataset = self._get_dataset(config.subset_name)

        return DataLoader(
            dataset=dataset,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            pin_memory=True,
            collate_fn=dataset.collate_fn,
            persistent_workers=config.num_workers > 0,
        )

    def test_dataloader(self) -> DataLoader:
        """Get test dataloader."""
        config = self.test_subset
        dataset = self._get_dataset(config.subset_name)

        return DataLoader(
            dataset=dataset,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            pin_memory=True,
            collate_fn=dataset.collate_fn,
            persistent_workers=config.num_workers > 0,
        )

    def predict_dataloader(self) -> DataLoader:
        """Get test dataloader."""
        config = self.test_subset
        dataset = self._get_dataset(config.subset_name)

        return DataLoader(
            dataset=dataset,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            pin_memory=True,
            collate_fn=dataset.collate_fn,
            persistent_workers=config.num_workers > 0,
        )

    def setup(self, stage: str) -> None:
        """Setup for each stage."""

    def teardown(self, stage: str) -> None:
        """Teardown for each stage."""
        # clean up after fit or test
        # called on every process in DDP

    @property
    def hparams_initial(self) -> AttributeDict:
        """The collection of hyperparameters saved with `save_hyperparameters()`. It is read-only.

        The reason why we override is that we have some custom resolvers for `DictConfig`.
        Some resolved Python objects has not a primitive type, so that is not loggable without errors.
        Therefore, we need to unresolve it this time.
        """
        hp = super().hparams_initial
        for key, value in hp.items():
            if isinstance(value, DictConfig):
                # It should be unresolved to make it loggable
                hp[key] = OmegaConf.to_container(value, resolve=False)

        return hp

    def __reduce__(self):
        """Re-initialize object when unpickled."""
        return (
            self.__class__,
            (
                self.task,
                self.data_format,
                self.data_root,
                self.train_subset,
                self.val_subset,
                self.test_subset,
                self.tile_config,
                self.image_color_channel,
                self.include_polygons,
                self.ignore_index,
                self.unannotated_items_ratio,
                self.auto_num_workers,
                self.device,
                self.input_size,
            ),
        )
