import copy
import logging
import os
import shutil
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Union, List, Callable, Tuple, Dict, Iterable, Any, Generator

import numpy as np
import pandas as pd
from lightning import LightningDataModule
from pandas import DataFrame
from torch.utils.data import DataLoader
from torchmetrics import MeanMetric
from tqdm import tqdm

from ..datasets.pandas_file_list_dataset import PandasFileListDataset
from ..types import PathLike, TensorOrNDArray
from ..utils import read_yaml, temp_directory, dump_yaml

logger = logging.getLogger(__name__)


def batched_df_pickles_iter(in_dir: Path, batch_size: int) -> DataFrame:
    """
    Loops over the files in in_dir and yields the data contained therein in batches of size batch_size

    Parameters
    ----------
    in_dir
        A directory containing a number of pickled pandas DataFrames named file_0.pkl ...
    batch_size
        The desired batch size

    Yields
    ------
    DataFrame
        A DataFrame containing batch_size rows except for the possible the last batch
    """
    batch = []
    batch_fill = 0
    num_pickles = len(list(in_dir.glob('file_*.pkl')))
    for file in tqdm([in_dir / f'file_{i}.pkl' for i in range(num_pickles)], desc="Looping through files for rebatch"):
        data = pd.read_pickle(file)
        used_data = 0
        while used_data < data.shape[0]:
            to_fill = min(data.shape[0] - used_data, batch_size - batch_fill)
            batch.append(data[used_data: used_data + to_fill])
            used_data += to_fill
            batch_fill += to_fill

            if batch_fill == batch_size:
                yield pd.concat(batch)
                batch = []
                batch_fill = 0

    if batch_fill > 0:
        yield pd.concat(batch)


class PandasDirDataModule(LightningDataModule):
    """
    A generic LightningDataModule implementation that accepts a directory of pickled pandas dataframes. The directory
    structure must contain a number of pickle files named 'file_{i}.pkl' numbered from 0 through N-1 and a metadata
    file named ds_info.yml which must contain at least a 'file_sizes' entry providing an ordered list of the number of
    samples in each file. E.g.

    file_sizes:
        - 10669194
        - 10669194

    The size of each file should be chosen such that the number of dataloader workers (train and validation) times the
    total in-memory size of the dataframe fits comfortably into memory on the device used for training.

    The total list of files is split up into a list of training and validation files according to the 'split' parameter.
    The first ceil(N * split) files are allocated for training and the remaining files are used for validation.
    As such one must be careful that the files partitioned in this way results in a sensible and unbiased
    train-validation split.

    The ds_info dictionary may also contain a lot of additional information useful for tracking the history of a dataset
    and the manipulations applied. As such the state of the dictionary may be important. It is recommended that all
    modifications to the dataset are performed through the transform method defined below and that a tag is provided
    with each modification. The full list of tags recording the state of the data is available through 'self.tags'.
    """
    def __init__(
        self,
        dataset_dir: PathLike,
        feature_cols: Optional[List[str]] = None,
        target_cols: Optional[Union[str, List[str]]] = None,
        weight_col: Optional[str] = None,
        split: float = 0.5,
        limit_files: Optional[int] = None,
        dataloader_kwargs: Optional[dict] = None,
        shuffle_in_train_files: bool = True,
    ):
        """
        Parameters
        ----------
        dataset_dir
            A path to a dataset directory structured as described in the class docstring
        feature_cols
            A list of the names of feature columns to provide when iterated over
        target_cols
            Optional. A list of names of columns to provide as targets when iterated over
        weight_col
            Optional. The name of a weight column to provide when iterated over
        split
            The train-validation split. The first ceil(N * split) files are allocated for training and the remaining
            files are used for validation
        limit_files
            Limit the number of files used to allow rapid testing
        dataloader_kwargs
            Any other arguments to be provided to DataLoader instances
        shuffle_in_train_files
            Whether to shuffle the data within each file during training
        """
        super().__init__()
        self.dataset_dir = Path(dataset_dir)
        self.feature_cols = feature_cols if feature_cols is not None else []
        self.target_cols = [target_cols] if isinstance(target_cols, str) else target_cols
        self.weight_col = weight_col
        self.split = split
        self.limit_files = limit_files
        self.shuffle_in_train_files = shuffle_in_train_files

        self.dataloader_kwargs = dataloader_kwargs or {}
        self.dataloader_kwargs.setdefault("batch_size", 2**15)
        self.dataloader_kwargs.setdefault("num_workers", os.cpu_count())
        if self.dataloader_kwargs["num_workers"] > 0:
            self.dataloader_kwargs.setdefault("persistent_workers", True)

    @property
    def all_files(self) -> List[Path]:
        """
        Returns
        -------
        List[Path]
            List of paths to all the files that comprise this dataset
        """
        files = [self.dataset_dir / f"file_{i}.pkl" for i in range(len(self.ds_info['file_sizes']))]
        if self.limit_files:
            return files[:self.limit_files]
        return files

    @property
    def num_train_files(self) -> int:
        """
        Returns
        -------
        int
            The number of train files in this dataset
        """
        return int(np.ceil(len(self.all_files) * self.split))

    @property
    def train_files(self):
        """
        Returns
        -------
        List[Path]
            List of paths to all the files containing train samples in this dataset
        """
        return self.all_files[:self.num_train_files]

    @property
    def validation_files(self):
        """
        Returns
        -------
        List[Path]
            List of paths to all the files containing validation samples in this dataset
        """
        return self.all_files[self.num_train_files:]

    @property
    def ds_info(self) -> Dict:
        """
        Returns
        -------
        Dict
            The contents of the ds_info.yml file
        """
        return read_yaml(self.dataset_dir / 'ds_info.yml')

    @property
    def all_data_ds(self) -> PandasFileListDataset:
        """
        Constructs a PandasFileListDataset for all files in the dataset (train and validation)
        """
        return PandasFileListDataset(
            self.all_files,
            self.feature_cols,
            self.target_cols,
            self.weight_col,
            file_sizes=self.file_sizes,
            shuffle_in_file=False,
        )

    @property
    def train_ds(self) -> PandasFileListDataset:
        """
        Constructs a PandasFileListDataset for the training files
        """
        return PandasFileListDataset(
            self.train_files,
            self.feature_cols,
            self.target_cols,
            self.weight_col,
            file_sizes=self.file_sizes[:len(self.train_files)],
            shuffle_in_file=self.shuffle_in_train_files,
        )

    @property
    def val_ds(self) -> PandasFileListDataset:
        """
        Constructs a PandasFileListDataset for the validation files
        """
        return PandasFileListDataset(
            self.validation_files,
            self.feature_cols,
            self.target_cols,
            self.weight_col,
            file_sizes=self.file_sizes[len(self.train_files):],
            shuffle_in_file=False,
        )

    @property
    def num_features(self) -> int:
        """
        The number of dimensions/features in the data
        """
        return len(self.feature_cols)

    @property
    def num_targets(self) -> int:
        """
        The number of target dimensions/features in the data
        """
        return len(self.target_cols)

    @property
    def file_sizes(self) -> List[int]:
        """
        List of the number of samples in each file
        """
        if self.limit_files:
            return self.ds_info['file_sizes'][:self.limit_files]
        return self.ds_info['file_sizes']

    @property
    def num_files(self) -> int:
        """
        Total number of train and validation files
        """
        return len(self.all_files)

    def open_file(self, idx: int) -> DataFrame:
        """
        Opens and returns the DataFrame in the file corresponding to the given index
        """
        return pd.read_pickle(self.all_files[idx])

    def all_dataloader(self) -> DataLoader:
        """
        Returns a DataLoader which iterates over all samples in all files
        """
        return DataLoader(
            self.all_data_ds,
            shuffle=False,
            **self.dataloader_kwargs,
        )

    def train_dataloader(self) -> DataLoader:
        """
        Returns a DataLoader which iterates over the samples in the training files
        """
        return DataLoader(
            self.train_ds,
            shuffle=False,
            **self.dataloader_kwargs,
        )

    def val_dataloader(self) -> DataLoader:
        """
        Returns a DataLoader which iterates over the samples in the validation files
        """
        return DataLoader(
            self.val_ds,
            shuffle=False,
            **self.dataloader_kwargs,
        )

    @property
    def tags(self) -> List[str]:
        """
        Returns
        -------
        List[str]
            The list of tags associated with the dataset
        """
        return self.ds_info.get('tags', [])

    def add_tag(self, tag: Union[str, List[str]]) -> None:
        """
        Adds a tag to the dataset

        Parameters
        ----------
        tag
            A tag or list of tags
        """
        if isinstance(tag, str):
            tag = [tag]
        new_ds_info = self.ds_info
        new_ds_info['tags'] = new_ds_info.get('tags', []) + list(tag)
        dump_yaml(new_ds_info, self.dataset_dir / 'ds_info.yml')

    def file_iter(
        self,
        include_train_files: bool = True,
        include_validation_files: bool = True,
    ) -> Iterable[Tuple[Path, DataFrame]]:
        """
        Yields the path and presiding dataframe for each file

        Parameters
        ----------
        include_train_files
        include_validation_files

        Yields
        ------
        Tuple[Path, DataFrame]
        """
        assert self.limit_files is None

        files = []
        if include_train_files:
            files += self.train_files
        if include_validation_files:
            files += self.validation_files

        for file in files:
            yield file, pd.read_pickle(file)

    def transform(
        self,
        transformation: Callable[[DataFrame], DataFrame],
        out_dir: Optional[PathLike],
        new_ds_info: dict = None,
        update_ds_info: dict = None,
        desc: Optional[str] = None,
        force: bool = False,
        tag: Union[str, List[str]] = None,
    ) -> "PandasDirDataModule":
        """
        Centralised function for manipulating the datasets. Ensures the state of ds_info is consistent. All
        modifications to a dataset should be performed through this function. Since all work is first completed in a
        temporary directory before being moved across to out_dir, data corruptions are unlikely if crashes occur

        Parameters
        ----------
        transformation
            A function that takes a dataframe and returns another dataframe with the desired modification
        out_dir
            The directory into which the new dataset should be saved. Can be None if the current dataset should be
            overwritten (must set force=True too)
        new_ds_info
            Manual override of the ds_info dictionary. The new file sizes and all tags will be inserted into this
            dictionary
        update_ds_info
            Information to update in the new ds_info dictionary. Information in the existing self.ds_info not
            overwritten in update_ds_info will be inherited and tags cannot be overwritten
        desc
            Description of the transformation for the loading bar
        force
            Overwrite any existing dataset with the path given in out_dir
        tag
            A tag (or list of tags) to add to the list of dataset tags to identify this transformation

        Returns
        -------
        PandasDirDataModule
            The new data module with the transformation applied
        """
        if desc is None and isinstance(tag, str):
            desc = f'Applying {tag}'
        desc = desc or 'Applying transformation'

        if out_dir is None:
            out_dir = self.dataset_dir
        out_dir = Path(out_dir)
        if out_dir.exists() and not force:
            raise Exception(f"{out_dir} already exists. Use `force' to overwrite.")

        old_file_sizes = self.file_sizes
        with temp_directory(out_dir.parent) as tmpdir:
            new_file_sizes = []
            for file, df in tqdm(self.file_iter(), desc=desc, total=self.num_files):
                new_df = transformation(df.copy())
                assert isinstance(new_df, pd.DataFrame)
                new_file_sizes.append(new_df.shape[0])
                pd.to_pickle(new_df, tmpdir / file.name)

            if new_ds_info is None:
                new_ds_info = copy.deepcopy(self.ds_info)
            if update_ds_info:
                new_ds_info.update(update_ds_info)
            new_ds_info['file_sizes'] = new_file_sizes
            dump_yaml(new_ds_info, tmpdir / 'ds_info.yml')

            if out_dir.exists():
                for path in out_dir.glob('file_*.pkl'):
                    path.unlink()
                if (out_dir / "ds_info.yml").exists():
                    (out_dir / "ds_info.yml").unlink()
            else:
                out_dir.mkdir()

            for file in tmpdir.glob("file_*.pkl"):
                shutil.move(file, out_dir / file.name)
            shutil.move(tmpdir / "ds_info.yml", out_dir / "ds_info.yml")

        print(f"Transformation complete from {self.dataset_dir} to {out_dir}")
        print(f"{sum(old_file_sizes)} data entries transformed into {sum(new_file_sizes)} data entries across {len(new_file_sizes)} files")

        new_dm = PandasDirDataModule(
            out_dir,
            self.feature_cols,
            self.target_cols,
            self.weight_col,
            split=self.split,
            dataloader_kwargs=self.dataloader_kwargs,
        )
        if tag is not None:
            new_dm.add_tag(tag)

        return new_dm

    @contextmanager
    def tmp_transform(self, transformation: Callable[[DataFrame], DataFrame]) -> Generator["PandasDirDataModule", None, None]:
        """
        Performs the given transformation using self.transform. The resulting datamodule is saved into a temporary
        directory that is deleted upon completion. Usage:

        dm = PandasDirDataModule(...)

        with dm.tmp_transform(transformation) as new_dm:
            ... do stuff with new_dm like train a network ...

        # the data in new_dm is now automatically deleted

        Arguments
        ---------
        transformation
            A function that takes a dataframe and returns another dataframe with the desired modification

        Yields
        ------
        PandasDirDataModule
            The new data module with the transformation applied in a temporary directory that is deleted upon exiting
            the context
        """
        with temp_directory() as tmpdir:
            new_dm = self.transform(transformation, tmpdir, force=True)
            yield new_dm

    def reweight(
        self,
        tag: str,
        reweight_fn: Callable[[DataFrame], TensorOrNDArray],
        out_dir: PathLike,
        force: bool = False,
        label_col: Optional[str] = None,
        output_weight_col: Optional[str] = None,
    ) -> "PandasDirDataModule":
        """
        Reweight the samples in the dataset according to the values given by reweight_fn

        Parameters
        ----------
        tag
            A short tag describing the reweighting
        reweight_fn
            A function that takes in a dataframe and returns an array of reweighting values such that the new weight for
            each sample is given by the old weight times the reweight value
        out_dir
            The directory into which the reweighted dataset should be written
        force
            Whether to overwrite any existing dataset that exists with the path out_dir
        label_col
            An optional column name for class labels. Weights are normalised within each class. If not provided, the
            average weight is normalised to 1.0 across the whole dataset
        output_weight_col
            The name of the column into which the new weight should be written. Defaults to self.weight_col if not
            provided. If self.weight_col is None, output_weight_col must be specified

        Returns
        -------
        PandasDirDataModule
            The reweighted dataset
        """
        weight_col = self.weight_col or output_weight_col
        output_weight_col = output_weight_col or self.weight_col
        if output_weight_col is None:
            raise ValueError(
                "If the dataset being reweighted does not already have a weight column, "
                "you must specify output_weight_col"
            )

        def reweight_wrapper(df):
            if output_weight_col not in df:
                logger.debug("Dataset seems unweighted. inserting 1.0 weights")
                df[output_weight_col] = 1.0
            df[output_weight_col] = df[weight_col] * reweight_fn(df)
            return df

        self.transform(
            reweight_wrapper,
            out_dir,
            force=force,
            tag=tag,
        )
        new_dm = PandasDirDataModule(
            dataset_dir=out_dir,
            feature_cols=self.feature_cols,
            target_cols=self.target_cols,
            weight_col=output_weight_col,
            split=self.split,
            dataloader_kwargs=self.dataloader_kwargs,
        )
        new_dm.normalise_weights(label_col)
        return self.copy(dataset_dir=out_dir, weight_col=output_weight_col)

    def normalise_weights(self, label_col: Optional[str] = None, output_weight_col: Optional[str] = None) -> None:
        """
        Normalises the weights in the dataset so the average weight is normalised to 1.0. If label_col is provided,
        the average weight is normalised to 1.0 within each class

        Parameters
        ----------
        label_col
            Optional name of the column which labels the class a given sample is from. If provided, the average weight
            within each class is set to 1 instead of the average weight over the whole dataset
        output_weight_col
            The column into which the normalised weight should be written. Defaults to self.weight_col and must be
            specified if self.weight_col is None
        """
        assert self.weight_col is not None
        output_weight_col = output_weight_col or self.weight_col

        weight_metrics = defaultdict(MeanMetric)
        for file, df in tqdm(self.file_iter(), desc="Calculating weight sums", total=self.num_files):
            if label_col is None:
                weight_metrics[0].update(df[self.weight_col].values)
            else:
                for label in np.unique(df[label_col]):
                    weight_metrics[label].update(df[self.weight_col][df[label_col].values == label].values)

        def normalise_wrapper(df):
            weights = df[self.weight_col].values

            if label_col is None:
                weights /= weight_metrics[0].compute()
            else:
                for label, metric in weight_metrics.items():
                    weights[df[label_col].values == label] /= metric.compute()

            df[output_weight_col] = weights
            return df

        self.transform(
            normalise_wrapper,
            self.dataset_dir,
            desc="Normalising weights",
            force=True,
        )

    def rebatch_files(self, new_file_size: int) -> None:
        """
        Re-arranges the data contained in dataset_dir, merging or splitting the constituent pandas dataframes so that
        all but the last dataframe has size new_file_size. Operation maintains order. Be careful not to accidentally mix
        training and validation data when using this function

        Parameters
        ----------
        new_file_size
            The desired new file size
        """
        new_file_size = int(new_file_size)
        assert new_file_size > 0
        logger.info(f"Original file sizes {self.ds_info['file_sizes']}")

        ds_info = self.ds_info
        new_batch_sizes = []
        for i, batch in enumerate(batched_df_pickles_iter(self.dataset_dir, new_file_size)):
            pd.to_pickle(batch, self.dataset_dir / f"file_{i}.pkl_")
            new_batch_sizes.append(batch.shape[0])
        ds_info['file_sizes'] = new_batch_sizes

        for file in self.all_files:
            file.unlink()
        for file in self.dataset_dir.glob("file_*.pkl_"):
            file.rename(self.dataset_dir / file.name[:-1])

        dump_yaml(ds_info, self.dataset_dir / 'ds_info.yml')
        logger.info(f"New file sizes {self.ds_info['file_sizes']}")
        self.add_tag("rebatched")

    def shuffle(self) -> None:
        """
        In-place shuffles all the data in dataset_dir randomly assigning each row to a new file and position in the
        file. The size of each file is not changed
        """
        rng = np.random.Generator(np.random.PCG64())
        in_files = list(self.dataset_dir.glob('file_*.pkl'))
        shuffled_sizes = np.zeros(len(in_files), dtype=int)
        new_ds_info = self.ds_info
        batch_sizes = np.asarray(self.ds_info["file_sizes"])

        for i, file in enumerate(tqdm(in_files, desc='Shuffling and splitting')):
            data = pd.read_pickle(file).sample(frac=1).reset_index(drop=True)
            partition = rng.multivariate_hypergeometric(batch_sizes - shuffled_sizes, data.shape[0])
            shuffled_sizes += partition

            cum_partition = np.cumsum(np.concatenate([[0], partition]))
            for j in range(len(in_files)):
                pd.to_pickle(data[cum_partition[j]: cum_partition[j + 1]], self.dataset_dir / f'{j}_{i}.pkl')

        new_file_sizes = []
        for j in tqdm(range(len(in_files)), desc='Merging and shuffling'):
            data = pd.concat([pd.read_pickle(self.dataset_dir / f'{j}_{i}.pkl') for i in range(len(in_files))])
            data = data.sample(frac=1).reset_index(drop=True)
            pd.to_pickle(data, self.dataset_dir / f'file_{j}.pkl')
            for i in range(len(in_files)):
                (self.dataset_dir / f'{j}_{i}.pkl').unlink()
            new_file_sizes.append(data.shape[0])

        new_ds_info['file_sizes'] = new_file_sizes
        dump_yaml(new_ds_info, self.dataset_dir / "ds_info.yml")
        self.add_tag("shuffled")

    def copy(self, **overrides) -> "PandasDirDataModule":
        """
        Creates a copy of the data module with the provided changes

        Parameters
        ----------
        overrides
            Any options to override in the copy. See the PandasDirDataModule constructor

        Returns
        -------
        PandasDirDataModule
            A copy of the dataset with the provided changes applied
        """
        arguments = {
            'dataset_dir': self.dataset_dir,
            'feature_cols': self.feature_cols,
            'target_cols': self.target_cols,
            'weight_col': self.weight_col,
            'split': self.split,
            'limit_files': self.limit_files,
            'dataloader_kwargs': self.dataloader_kwargs,
        }
        arguments.update(overrides)
        return PandasDirDataModule(**arguments)

    def merge(
        self,
        others: Union[Iterable["PandasDirDataModule"], "PandasDirDataModule"],
        out_dir: PathLike,
        label_col: Optional[str] = None,
        labels: Optional[Iterable[Any]] = None,
        force: bool = False,
    ) -> "PandasDirDataModule":
        """
        Merges this dataset with the provided others

        Parameters
        ----------
        others
            A sequence of other PandasDirDataModule instances
        out_dir
            The directory into which the merged dataset should be written
        label_col
            Optional label_col used to label which dataset each sample originated from
        labels
            If label_col is provided, these labels are used as the values for each dataset. Must be a sequence of length
            len(others) + 1. The first label corresponds to this dataset and the remainder are paired up in order with
            the others
        force
            Whether to overwrite existing files in the out_dir

        Returns
        -------
        PandasDirDataModule
            The merged dataset
        """
        from .pandas_directory_data_module_builder import PandasDirDataModuleBuilder

        others = others if isinstance(others, Iterable) else [others]
        if labels is None:
            assert label_col is None
            labels = list(range(len(others) + 1))
        assert len(labels) == len(others) + 1

        out_dir = Path(out_dir)

        with PandasDirDataModuleBuilder(
            out_dir,
            force=force,
            shuffle=False,
            tags=[f'merged from {dm.dataset_dir}' for dm in [self, *others]],
        ) as builder:
            for label, dm in tqdm(zip(labels, [self, *others]), desc='Merging datasets', total=len(others)+1):
                for file in tqdm(dm.all_files, total=dm.num_files, leave=False, desc=f'Copying files'):
                    df = pd.read_pickle(file)
                    if label_col is not None:
                        df[label_col] = label

                    builder.write(df)

        new_dm = PandasDirDataModule(
            dataset_dir=out_dir,
            feature_cols=self.feature_cols,
            target_cols=self.target_cols,
            weight_col=self.weight_col,
            split=self.split,
            limit_files=self.limit_files,
            dataloader_kwargs=self.dataloader_kwargs,
        )

        return new_dm


