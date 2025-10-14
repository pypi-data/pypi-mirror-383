from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from daxs.correctors import ConcentrationCorrectionError, SimpleConcentrationCorrector
from daxs.measurements import Measurement1D, Rixs
from daxs.scans import Scan, Scans
from daxs.sources import Hdf5Source
from daxs.utils import resources


def test_simple_concentration_correction_mock():
    # The same number of scans and points in the concentration correction scan.
    conc_corr_scan = Scan(np.array([1, 1]), np.array([0.5, 1.0]))
    corrector = SimpleConcentrationCorrector(conc_corr_scan)
    scans = [
        Scan(np.array([1, 1, 1]), np.array([1.0, 2.0, 3.0])),
        Scan(np.array([1, 1, 1]), np.array([4.0, 5.0, 6.0])),
    ]
    scans = Scans(scans)
    corrector.apply(scans)
    assert np.allclose(scans[0].signal, np.array([2, 4, 6]))
    assert np.allclose(scans[1].signal, np.array([4, 5, 6]))

    scans[0].monitor = np.array([10, 20, 30])
    conc_corr_scan.monitor = np.array([100, 200])
    corrector.apply(scans)
    assert np.allclose(scans[0].monitor, np.array([0.1, 0.2, 0.3]))

    # Different number of scans and points in the concentration correction scan.
    # The concentration correction scan has the same number of points as the scans.
    scans.reset()
    conc_corr_scan = Scan(np.array([1, 1, 1]), np.array([0.5, 1.0, 2.0]))
    corrector = SimpleConcentrationCorrector(conc_corr_scan)
    corrector.apply(scans)
    assert np.allclose(scans[0].signal, np.array([2, 2, 1.5]))
    assert np.allclose(scans[1].signal, np.array([8, 5, 3]))

    # The number of scans and concentration correction scans is the same.
    scans.reset()
    conc_corr_scans = [
        Scan(np.array([1, 1, 1]), np.array([0.5, 1.0, 2.0])),
        Scan(np.array([1, 1, 1]), np.array([1.0, 2.0, 3.0])),
    ]
    conc_corr_scans = Scans(conc_corr_scans)
    corrector = SimpleConcentrationCorrector(conc_corr_scans)
    corrector.apply(scans)
    assert np.allclose(scans[0].signal, np.array([2, 2, 1.5]))
    assert np.allclose(scans[1].signal, np.array([4, 2.5, 2]))


@pytest.mark.parametrize(
    ("scan_ids,conc_corr_ids,expected"),
    (
        ([4], [5], [0.0750053, 0.06380908]),
        ([4, 10], [5, 11], [0.07468005, 0.06404491]),
        ([4], [6], ConcentrationCorrectionError),
        ([4, 10], [5, 11, 12], ConcentrationCorrectionError),
    ),
)
def test_simple_concentration_correction_equal_number_of_scans(
    scan_ids: list[int], conc_corr_ids: list[int], expected: Any
):
    hdf5_path: str = resources.getfile("A1_Kb_XES.h5")
    data_mappings = {
        "x": ".1/measurement/xes_en",
        "signal": ".1/measurement/det_dtc_apd",
        "monitor": ".1/measurement/I02",
    }

    source = Hdf5Source(hdf5_path, scan_ids, data_mappings=data_mappings)
    measurement = Measurement1D(source)
    if isinstance(expected, list):
        measurement.concentration_correction(conc_corr_ids)
        assert measurement.signal[-2:] == pytest.approx(expected)
    else:
        with pytest.raises(expected):
            measurement.concentration_correction(conc_corr_ids)


def test_simple_concentration_correction_equal_number_of_scans_and_points():
    hdf5_path = resources.getfile("Fe2O3_Ka1Ka2_RIXS.h5")
    data_mappings = {
        "x": ".1/measurement/zaptime",
        "y": ".1/instrument/positioners/xes_en",
        "signal": [".1/measurement/det_dtc_apd"],
        "monitor": ".1/measurement/I02",
    }
    source = Hdf5Source(hdf5_path, list(range(4, 225)), data_mappings=data_mappings)
    measurement = Rixs(source)
    measurement.concentration_correction([225])
    assert measurement.scans[0].signal[-1] == pytest.approx(0.01887687)
    assert measurement.scans[-1].monitor[0] == pytest.approx(0.24412638)
    assert measurement.signal.mean() == pytest.approx(0.02197076489)
