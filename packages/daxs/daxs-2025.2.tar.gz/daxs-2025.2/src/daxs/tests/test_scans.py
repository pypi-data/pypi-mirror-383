from __future__ import annotations

import copy
import os
import tempfile
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pytest

from daxs.measurements import Measurement
from daxs.scans import Scan
from daxs.sources import Hdf5Source
from daxs.utils import resources


@pytest.fixture
def scan():
    x = np.array([3, 1, 2, 0, 4])
    signal = np.array([[2, 9, 0, 4, 1], [9, 1, 3, 4, 3]])
    data = {
        "monitor": np.array([1, 1, 2, 4, 2]),
        "detection_time": [0.2, 0.2, 0.2, 0.2, 0.2],
        "filename": "No file name",
        "index": 1,
    }
    scan = Scan(x, signal, data=data)
    return scan


def test_scan_init():
    rng = np.random.default_rng()
    x = rng.random(10)
    signal = "not an array"

    with pytest.raises(TypeError):
        Scan(x, signal)  # type: ignore


def test_scan_reset(scan: Scan):
    scan.x = np.array([1, 1, 1, 1, 1])
    scan.reset()
    assert scan.x == pytest.approx([0, 1, 2, 3, 4])


def test_scan_properties(scan: Scan):
    assert scan.x == pytest.approx([0, 1, 2, 3, 4])
    assert scan.signal == pytest.approx([4.0, 5.0, 1.5, 5.5, 2.0])
    assert scan.monitor == pytest.approx([4, 1, 2, 1, 2])

    scan.x = np.array([3, 1, 2, 0, 4])
    assert scan.x == pytest.approx([0, 1, 2, 3, 4])
    assert scan.signal == pytest.approx([4.0, 5.0, 1.5, 5.5, 2.0])

    scan.reset()
    scan.x = np.array([5, 6, 7, 9, 11])
    assert scan.x == pytest.approx([5, 6, 7, 9, 11])
    assert scan.signal == pytest.approx([4.0, 5.0, 1.5, 5.5, 2.0])

    scan.reset()
    with pytest.raises(ValueError):
        scan.x = np.array([5, 6, 7, 9, 11, 12])

    scan.reset()
    scan.x = np.array([0, 1, 2, 3, 5, 10])
    assert scan.x == pytest.approx([0, 1, 2, 3, 5, 10])
    assert scan.signal == pytest.approx(
        [4.0, 5.0, 1.5, 5.5, np.nan, np.nan], nan_ok=True
    )


def test_scan_interpolate(scan: Scan):
    scan._signal = np.array([])
    with pytest.raises(ValueError):
        rng = np.random.default_rng()
        scan.interpolate(a=rng.random(10))


def test_scan_outliers_removal(scan: Scan):
    scan.remove_outliers(method="hampel")
    assert scan.signal == pytest.approx([4.0, 5.0, 1.5, 2.5, 2.0])


def test_scan_dead_time_correction(scan: Scan):
    with pytest.raises(TypeError):
        scan.dead_time_correction()  # type: ignore

    tau = np.array([1.0, 1.0, 1.0], dtype=np.float64) * 1e-3
    with pytest.raises(ValueError):
        scan.dead_time_correction(tau=tau)

    scan.reset()
    tau = np.array([1.0, 1.0]) * 1e-3
    scan.dead_time_correction(tau)
    assert scan.signal == pytest.approx(
        np.array([4.08163265, 5.21455445, 1.52284264, 5.72214289, 2.0253552])
    )

    scan.reset()
    scan.data.pop("detection_time", None)
    with pytest.raises(ValueError):
        scan.dead_time_correction(tau)

    with pytest.raises(ValueError):
        scan.dead_time_correction(tau=tau, detection_time=0.0)

    with pytest.raises(ValueError):
        scan.dead_time_correction(tau=[1.0, 1.0], detection_time=2)


def test_scan_plot(scan: Scan):
    _, ax = plt.subplots()
    scan.remove_outliers(method="hampel")
    scan.plot(ax)


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_scan_divide_by_scan(scan: Scan):
    scan1 = copy.deepcopy(scan)
    scan2 = copy.deepcopy(scan)

    scan2.divide_by_scan(scan1)
    scan2._signal = scan2._signal / 2.0  # type: ignore
    assert scan2.signal[0:2] == pytest.approx([0.5, 0.5])


def test_str(scan: Scan):
    assert str(scan) == "None/None"


@pytest.fixture()
def hdf5_filename():
    return resources.getfile("Pd_foil_La_XANES.h5")


@pytest.fixture()
def data_mappings():
    return {
        "x": ".1/measurement/hdh_angle",
        "signal": [".1/measurement/g09", ".1/measurement/g14"],
    }


def test_scans_get_common_axis(hdf5_filename: str, data_mappings: dict[str, Any]):
    source = Hdf5Source(hdf5_filename, [3], data_mappings=data_mappings)
    measurement = Measurement(source)
    values = measurement.scans.get_common_axis("x")
    assert np.all(values == getattr(measurement.scans[0], "x"))

    source = Hdf5Source(hdf5_filename, [3, 4, 7, 8, 9], data_mappings=data_mappings)
    measurement = Measurement(source)

    values = measurement.scans.get_common_axis("x")
    assert values[-1] == pytest.approx(38.72936736)

    values = measurement.scans.get_common_axis("x", mode="union")
    assert values[-1] == pytest.approx(38.72939236)


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_scan_divide_by_scan_inf(scan: Scan):
    scan1 = copy.deepcopy(scan)
    scan2 = copy.deepcopy(scan)
    scan2._signal = np.zeros_like(scan2._signal)

    with pytest.raises(
        ValueError, match=r"Cannot divide by signal with all zero values."
    ):
        scan1.divide_by_scan(scan2)


def test_scan_aggregation_error(scan: Scan):
    with pytest.raises(ValueError, match=r"Unknown aggregation method 'unknown'"):
        scan.aggregation = "unknown"


def test_scan_aggregation_methods(scan: Scan):
    scan.aggregation = "sum"
    assert scan.signal == pytest.approx(np.nansum(scan._signal, axis=0))

    scan.aggregation = "median"
    assert scan.signal == pytest.approx(np.nanmedian(scan._signal, axis=0))

    scan.aggregation = "mean"
    assert scan.signal == pytest.approx(np.nanmean(scan._signal, axis=0))


@pytest.fixture
def temp_file_single_row():
    """Fixture for temp file with single row."""
    data = "1.0\t2.0\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(data)
        temp_file = f.name
    yield temp_file
    os.unlink(temp_file)


def test_from_txt_success():
    """Test successful creation of Scan from text file."""
    data = "1.0\t2.0\t3.0\n4.0\t5.0\t6.0\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(data)
        temp_file = f.name

    try:
        data_mappings = {"x": 0, "signal": 1}
        scan = Scan.from_txt(temp_file, data_mappings)
        assert scan.filename == temp_file
        np.testing.assert_array_equal(scan.x, [1.0, 4.0])
        np.testing.assert_array_equal(scan.signal, [2.0, 5.0])
    finally:
        os.unlink(temp_file)


def test_from_txt_missing_required_key(temp_file_single_row: str):
    """Test error when required key is missing from data_mappings."""
    # Missing "signal" key.
    data_mappings = {"x": 0}

    with pytest.raises(
        ValueError,
        match=r"The data_mappings must contain an entry for signal.",
    ):
        Scan.from_txt(temp_file_single_row, data_mappings)


def test_from_txt_file_not_found():
    """Test error when file does not exist."""
    data_mappings = {"x": 0, "signal": 1}

    with pytest.raises(
        ValueError,
        match=r"Error reading data from file nonexistent.txt.",
    ):
        Scan.from_txt("nonexistent.txt", data_mappings)


def test_from_txt_column_out_of_range(temp_file_single_row: str):
    """Test error when column index is out of range."""
    # Column 2 does not exist (only 0 and 1).
    data_mappings = {"x": 0, "signal": 2}

    with pytest.raises(
        ValueError,
        match=r"Error reading data from file.",
    ):
        Scan.from_txt(temp_file_single_row, data_mappings)


def test_from_txt_with_delimiter():
    """Test reading with custom delimiter."""
    # Create a temporary text file with comma-separated data.
    data = "1.0,2.0,3.0\n4.0,5.0,6.0\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(data)
        temp_file = f.name

    try:
        data_mappings = {"x": 0, "signal": 1}
        scan = Scan.from_txt(temp_file, data_mappings, delimiter=",")
        np.testing.assert_array_equal(scan.x, [1.0, 4.0])
        np.testing.assert_array_equal(scan.signal, [2.0, 5.0])
    finally:
        os.unlink(temp_file)


def test_from_txt_with_skiprows():
    """Test reading with skiprows."""
    # Create a temporary text file with comment line.
    data = "# Comment\n1.0\t2.0\n4.0\t5.0\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(data)
        temp_file = f.name

    try:
        data_mappings = {"x": 0, "signal": 1}
        scan = Scan.from_txt(temp_file, data_mappings, skiprows=1)
        np.testing.assert_array_equal(scan.x, [1.0, 4.0])
        np.testing.assert_array_equal(scan.signal, [2.0, 5.0])
    finally:
        os.unlink(temp_file)


def test_read_data_at_paths_key_error(hdf5_filename: str):
    """Test KeyError when data path does not exist."""
    with pytest.raises(KeyError, match=r"Unable to access .*::/.*nonexistent_path"):
        Scan.read_data_at_paths(hdf5_filename, 3, "nonexistent_path")


def test_read_data_at_paths_success(hdf5_filename: str):
    """Test successful reading of data."""
    data = Scan.read_data_at_paths(hdf5_filename, 3, ".1/measurement/hdh_angle")
    assert isinstance(data, np.ndarray)
    assert data.size > 0
