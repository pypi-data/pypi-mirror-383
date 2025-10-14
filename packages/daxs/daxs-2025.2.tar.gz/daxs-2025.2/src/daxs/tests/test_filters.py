from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from daxs.scans import Scan, Scans

import numpy as np
import pytest

from daxs.filters import hampel
from daxs.sources import Hdf5Source
from daxs.utils import resources


@pytest.fixture
def scans() -> Scans:
    filename = resources.getfile("Pd_foil_La_XANES.h5")
    data_mappings = {
        "x": ".1/measurement/hdh_angle",
        "signal": [".1/measurement/g09", ".1/measurement/g14"],
    }
    source = Hdf5Source(filename, 5, data_mappings=data_mappings)
    return source.scans


@pytest.mark.parametrize("indices, values", [(69, 14111.5)])
def test_hampel(scans: list[Scan], indices: int, values: float):
    [scan] = scans
    outliers, medians = hampel(scan.signal, window_size=5, threshold=3.5, axis=0)
    assert outliers[indices]
    assert medians[indices] == pytest.approx(values, abs=np.finfo(float).eps)

    outliers, medians = hampel(scan.signal, window_size=20, threshold=3.5, axis=0)
    assert not outliers[indices]
