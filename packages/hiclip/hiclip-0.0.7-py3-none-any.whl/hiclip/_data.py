import warnings
from typing import Optional

import anndata
import cooler
import numpy as np
from anndata import AnnData
from scvi import settings
from scvi.data import AnnDataManager
from scvi.dataloaders import DataSplitter
from scvi.model._utils import parse_device_args
from tqdm import tqdm

from ._utils import coarsen


def _rename_chroms(c: cooler.Cooler, characters: str = "chr"):
    _rename_dict = {}
    for chromname in c.chromnames:
        if chromname.startswith(characters):
            _rename_dict[chromname] = chromname[len(characters) :]
    if _rename_dict:
        warnings.warn(
            "HiClip package will automatically remove 'chr' prefix from chromnames "
            + "in all accessed cooler files. This may cause concurrency issues if multiple "
            + "processes are accessing the same cooler file simultaneously.",
            UserWarning,
            stacklevel=2,
        )
        cooler.rename_chroms(c, _rename_dict)


def _get_contact(
    c: cooler.Cooler,
    chrom1: str,
    start1: int,
    end1: int,
    chrom2: str = None,
    start2: int = None,
    end2: int = None,
) -> np.array:
    region1 = "{}:{}-{}".format(chrom1, start1, end1)
    region2 = (
        "{}:{}-{}".format(chrom2, start2, end2) if chrom2 and start2 and end2 else None
    )

    mat = c.matrix(balance=False).fetch(region1, region2)
    return mat


def _get_cools(*cooler_uris):
    cools = [cooler.Cooler(cooler_uri) for cooler_uri in cooler_uris]
    for c in cools:
        _rename_chroms(c)

    return tuple(cools)


def setup_data(
    main_cooler_uri: str,
    sub_cooler_uri: str,
    target_cooler_uri: str,
    n_bin: int = 400,
    step_bin: int = 200,
    nonzero_ratio: float = 0.001,
) -> AnnData:
    """Setup function.

    Parameters
    ----------
    main_path
        # TODO
    sub_path
        # TODO
    target_path
        # TODO

    Returns
    -------
    An :class:`~anndata.AnnData` object containing the data required for model training.
    """
    main_c, sub_c, target_c = _get_cools(
        main_cooler_uri, sub_cooler_uri, target_cooler_uri
    )
    assert main_c.binsize == sub_c.binsize == target_c.binsize

    binsize = main_c.binsize
    chroms = set(main_c.chromnames) & set(sub_c.chromnames) & set(target_c.chromnames)

    datas = None
    for chrom in chroms:
        _datas = None
        chromsize = min(
            main_c.chromsizes[chrom],
            sub_c.chromsizes[chrom],
            target_c.chromsizes[chrom],
        )
        for i in tqdm(
            range(0, chromsize, step_bin),
            total=int(chromsize / step_bin / binsize - 1),
            desc=chrom,
        ):
            start, end = i * binsize, (i + n_bin) * binsize
            if end > chromsize:
                break

            _main = _get_contact(main_c, chrom, start, end)
            _sub = _get_contact(sub_c, chrom, start, end)
            _target = _get_contact(target_c, chrom, start, end)

            if nonzero_ratio > np.count_nonzero(_target) / np.size(_target):
                continue

            _fuzzy_main = coarsen(_main)

            data = AnnData(
                X=_fuzzy_main.flatten()[np.newaxis, :],
                layers={
                    "main(source)": _main.flatten()[np.newaxis, :],
                    "sub": _sub.flatten()[np.newaxis, :],
                    "target": _target.flatten()[np.newaxis, :],
                },
            )
            data.obs_names = ["{}:{}-{}".format(chrom, start, end)]
            _datas = anndata.concat([_datas, data]) if _datas else data
        if _datas is None:
            continue
        datas = anndata.concat([datas, _datas]) if datas else _datas

    return datas


class AnnDataSplitter(DataSplitter):
    """Creates data loaders ``train_set``, ``validation_set``, ``test_set`` using given indices."""

    def __init__(
        self,
        adata_manager: AnnDataManager,
        train_indices,
        valid_indices,
        test_indices,
        accelerator: str = "auto",
        **kwargs,
    ):
        super().__init__(adata_manager)
        self.data_loader_kwargs = kwargs
        self.accelerator = accelerator
        self.train_idx = train_indices
        self.val_idx = valid_indices
        self.test_idx = test_indices

    def setup(self, stage: Optional[str] = None):
        """Over-ride parent's setup to preserve split idx."""
        accelerator, _, self.device = parse_device_args(
            self.accelerator, return_device="torch"
        )
        self.pin_memory = (
            True
            if (settings.dl_pin_memory_gpu_training and accelerator == "gpu")
            else False
        )
