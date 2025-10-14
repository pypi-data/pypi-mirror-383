"""The module provides classes for the representation of scans in measurements."""

from __future__ import annotations

import copy
import logging
import os
from typing import TYPE_CHECKING, Any, Iterable

if TYPE_CHECKING:
    from matplotlib.axes import Axes

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt

from daxs.config import Config
from daxs.filters import hampel
from daxs.utils import arrays

logger = logging.getLogger(__name__)

use_blissdata_api = Config().get("use_blissdata_api", False)
if use_blissdata_api:
    from blissdata.h5api.dynamic_hdf5 import File
else:
    from silx.io.h5py_utils import File


class Scan:
    def __init__(
        self,
        x: npt.NDArray[np.float64],
        signal: npt.NDArray[np.float64],
        *,
        data: dict[Any, Any] | None = None,
    ) -> None:
        """Define the base representation of scans in measurements.

        Args:
            x: X-axis values (1D array).
            signal: Signal values (1D or 2D array). For a 2D array, the components
                are stored as rows. A 1D array will be converted to
                a 2D array.
            y: Y-axis values (1D array).
            monitor: Monitor values (1D array).
            data: Storage for the raw scan data and metadata.
        """
        # Initialize metadata
        self._filename: str | None = None
        self._index: int | None = None
        self._aggregation: str = "mean"

        # Initialize data storage
        self._data = {} if data is None else data.copy()

        # Initialize working arrays.
        self._x = np.array([])
        self._y = np.array([])
        self._signal = np.array([])
        self._monitor = np.array([])

        # Initialize processing arrays.
        self._indices: npt.NDArray[np.int32] = np.array([])
        self.outliers: npt.NDArray[np.bool_] = np.array([])
        self.medians: npt.NDArray[np.float64] = np.array([])

        # Set values through properties.
        self.x = x
        self.signal = signal
        for attr in ("y", "monitor"):
            if attr in self._data:
                setattr(self, attr, self._data[attr])

        # Reindex the data after the initial assignment.
        self.reindex()

    @classmethod
    def from_data(cls, data: dict[Any, Any]) -> Scan:
        """Create a scan from a data dictionary.

        Args:
            data: Dictionary containing at least the keys "x" and "signal".

        Returns:
            A new Scan instance.

        Raises:
            ValueError: If required keys are missing from the provided dictionary.
        """
        try:
            x = data["x"]
            signal = data["signal"]
        except KeyError as e:
            raise ValueError(f"Missing required key in data dictionary: {e}") from e

        return cls(x=x, signal=signal, data=data)

    @classmethod
    def from_hdf5(
        cls, filename: str, index: int, data_mappings: dict[str, Any]
    ) -> Scan:
        """Create a scan by reading data from an HDF5 file.

        Args:
            filename: Path to the HDF5 file.
            index: Scan index in the file.
            data_mappings: Dictionary mapping scan attributes to file paths.
                Must contain entries for 'x' and 'signal'.

        Returns:
            A new Scan instance loaded from the file.

        Raises:
            ValueError: If required keys are missing from data_mappings.
        """
        for key in ("x", "signal"):
            if key not in data_mappings:
                raise ValueError(f"The data_mappings must contain an entry for {key}.")

        # Read all data into a dictionary.
        data = {}
        for key, data_paths in data_mappings.items():
            data[key] = cls.read_data_at_paths(filename, index, data_paths)

        scan = cls.from_data(data)
        scan.filename = filename
        scan.index = index

        return scan

    @classmethod
    def from_txt(
        cls,
        filename: str,
        data_mappings: dict[str, int],
        **kwargs: Any,
    ) -> Scan:
        """Create a scan by reading data from a text file.

        Args:
            filename: Path to the text file.
            data_mappings: Dictionary mapping scan attributes to column indices.
                Must contain entries for "x" and "signal". Column indices are 0-based.
            **kwargs: Additional keyword arguments passed to np.loadtxt, e.g.,
                delimiter, skiprows, etc.

        Returns:
            A new Scan instance loaded from the text file.

        Raises:
            ValueError: If required keys are missing from data_mappings or if there
                are issues reading data from the file.
        """
        for key in ("x", "signal"):
            if key not in data_mappings:
                raise ValueError(f"The data_mappings must contain an entry for {key}.")

        try:
            kwargs["usecols"] = list(data_mappings.values())
            data = np.loadtxt(filename, **kwargs)
        except Exception as e:
            raise ValueError(f"Error reading data from file {filename}: {e}")

        # Convert the data array to a dictionary where the keys are from data_mappings.
        try:
            data = {key: data[:, index] for key, index in data_mappings.items()}
        except IndexError as e:
            raise ValueError(f"Column index out of range in data_mappings: {e}") from e

        scan = cls.from_data(data)
        scan.filename = filename

        return scan

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, a: npt.NDArray[np.float64]) -> None:
        """Set the X-axis values.

        Several cases are considered:

        1. The new values are the same as the current ones. In this case, nothing has
           to be done.
        2. The limits of the new values are within the current values. In this case,
           the signal and monitor data are interpolated to the new X-axis values.
        3. The new values are outside the current values, but the two arrays have the
           same shape. In this case, the new values are assigned to the X-axis. It
           is useful when the X-axis changes to different units, e.g., angle to energy.
        4. The new values are outside the current values and of different shapes. In
           this case, an error is raised.

        Args:
            a: The new X-axis values to set.

        Raises:
            TypeError: If the input is not a NumPy array.
            ValueError: If the new values are invalid or incompatible.
        """
        if not isinstance(a, np.ndarray):
            raise TypeError("The X-axis values must be a NumPy array.")

        if a.size == 0:
            raise ValueError("The X-axis values must not be empty.")

        # Initial assignment.
        if self._x.size == 0:
            if "x" not in self._data:
                self._data["x"] = a.copy()
            self._x = a.astype(np.float64)
            return

        a = np.sort(a, kind="stable")

        if np.array_equal(self._x, a):
            logger.debug(
                "The new X-axis values are the same as the current ones in %s.",
                self.label,
            )
            return

        if arrays.intersect(a, self._x).size > 0:
            self.interpolate(a)
            return

        if self._x.size == a.size:
            logger.debug("Assigning the new X-axis values.")
            self._x = a.astype(np.float64)
            self._indices = np.array([])
            return

        raise ValueError(
            "The new X-axis values are outside the current ones. "
            f"Current X-axis limits: {self._x[0]:.6f} and {self._x[-1]:.6f}, "
            f"new X-axis limits: {a[0]:.6f} and {a[-1]:.6f}."
        )

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, a: npt.NDArray[np.float64]) -> None:
        """Set the Y-axis values.

        Args:
            a: Y-axis values (1D array).

        Raises:
            TypeError: If the input is not a NumPy array.
        """
        if not isinstance(a, np.ndarray):
            raise TypeError("The Y-axis values must be a NumPy array.")

        if a.size == 0:
            logger.debug("Setting empty Y-axis values.")
            self._y = np.array([])
            return

        if "y" not in self._data:
            self._data["y"] = a.copy()

        self._y = a.astype(np.float64)

    @property
    def signal(self):
        # Return an empty array if the signal is empty to avoid errors when aggregating.
        if self._signal.size == 0:
            return self._signal

        methods = {
            "mean": np.nanmean,
            "sum": np.nansum,
            "median": np.nanmedian,
        }

        method = methods.get(self.aggregation)
        if method is None:
            raise ValueError(f"Unknown aggregation method {self.aggregation}.")

        return method(self._signal, axis=0)

    @signal.setter
    def signal(self, a: npt.NDArray[np.float64]) -> None:
        """Set the signal values.

        Args:
            a: Signal values (1D or 2D array). For a 2D array, the components are
                stored as rows. A 1D array will be converted to a 2D array.

        Raises:
            TypeError: If the input is not a NumPy array.
            ValueError: If the signal is invalid or incompatible with the current
              X-axis.
        """
        if not isinstance(a, np.ndarray):
            raise TypeError("The signal values must be a NumPy array.")

        if a.size == 0:
            raise ValueError("The signal values must not be empty.")

        if a.ndim not in (1, 2):
            raise ValueError("The signal must be a 1D or a 2D array.")

        # Enforce that X-axis is set before assigning the signal.
        if self._x.size == 0:
            raise ValueError("The X-axis must be set before assigning the signal.")

        # For initial assignment, validate against x if it is already set.
        if self._x.size > 0 and self._x.size != a.shape[-1]:
            raise ValueError(
                f"The signal size ({a.shape[-1]}) must match the "
                f"X-axis size ({self._x.size})."
            )

        if "signal" not in self._data:
            self._data["signal"] = a.copy()

        # Convert 1D signal to 2D for consistent internal representation.
        if a.ndim == 1:
            a = a[np.newaxis, :]

        self._signal = a.astype(np.float64)

    @property
    def monitor(self):
        return self._monitor

    @monitor.setter
    def monitor(self, a: npt.NDArray[np.float64]) -> None:
        """Set the monitor values.

        Args:
            a: Monitor values (1D array).

        Raises:
            TypeError: If the input is not a NumPy array.
            ValueError: If the array size does not match the X-axis size.
        """
        # Validate input type.
        if not isinstance(a, np.ndarray):
            raise TypeError("The monitor values must be a NumPy array.")

        if a.size == 0:
            logger.debug("Setting empty monitor values.")
            self._monitor = np.array([])
            return

        # Validate size compatibility with X-axis.
        if self._x.size > 0 and a.size != self._x.size:
            raise ValueError(
                f"The monitor size ({a.size}) must match the "
                f"X-axis size ({self._x.size})."
            )

        if "monitor" not in self._data:
            self._data["monitor"] = a.copy()

        self._monitor = a.astype(np.float64)

    @property
    def indices(self):
        return self._indices

    @indices.setter
    def indices(self, a: npt.NDArray[np.int32]) -> None:
        """Set the indices array.

        Args:
            a: Indices array (1D array).

        Raises:
            TypeError: If the input is not a NumPy array.
            ValueError: If the indices array shape does not match the X-axis shape.
        """
        if not isinstance(a, np.ndarray):
            raise TypeError("The indices must be a Numpy array.")

        if a.shape != self._x.shape:
            raise ValueError("The indices and X-axis arrays must have the same shape.")

        self._indices = a.astype(np.int32)
        self.reindex()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data: dict[Any, Any]) -> None:
        """Set the data dictionary."""
        if not isinstance(data, dict):
            raise TypeError("The data must be a dictionary.")
        self._data = data
        self.reset()

    @property
    def label(self) -> str:
        return f"{self.filename}/{self.index}"

    @property
    def filename(self) -> str | None:
        """The filename associated with this scan."""
        return self._filename

    @filename.setter
    def filename(self, value: str | None) -> None:
        """Set the filename associated with this scan.

        Args:
            value: The filename to set. If not None, the file must exist.

        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
        if value is not None and not os.path.exists(value):
            raise FileNotFoundError(f"The file '{value}' does not exist.")
        self._filename = value

    @property
    def index(self) -> int | None:
        """The index of this scan within its file."""
        return self._index

    @index.setter
    def index(self, value: int | None) -> None:
        """Set the index of this scan.

        Args:
            value: The index to set. Must be a non-negative integer or None.

        Raises:
            TypeError: If the value is not an integer or None.
            ValueError: If the value is a negative integer.
        """
        if value is not None:
            if not isinstance(value, int):
                raise TypeError("The index must be an integer or None.")
            if value < 0:
                raise ValueError("The index must be a non-negative integer.")
        self._index = value

    @property
    def aggregation(self) -> str:
        """The aggregation method used for signal processing."""
        return self._aggregation

    @aggregation.setter
    def aggregation(self, value: str) -> None:
        """Set the aggregation method for signal processing.

        Args:
            value: The aggregation method to set.

        Raises:
            TypeError: If the value is not a string.
            ValueError: If the aggregation method is not supported.
        """
        if not isinstance(value, str):
            raise TypeError("The aggregation method must be a string.")

        methods = ("mean", "sum", "median")
        if value not in methods:
            raise ValueError(
                f"Unknown aggregation method '{value}'. "
                f"Supported methods: {', '.join(methods)}."
            )
        self._aggregation = value

    def reset(self) -> None:
        """Reset the scan data to the values stored in the data dictionary.

        Raises:
            KeyError: If required data is missing from the internal dictionary.
        """
        try:
            x = self._data["x"]
            signal = self._data["signal"]
        except KeyError as e:
            raise KeyError(
                "Cannot reset: missing required data in internal dictionary."
            ) from e

        # Reset working arrays directly from stored data.
        self._x = x.astype(np.float64)
        self._signal = signal.astype(np.float64)

        # Convert 1D signal to 2D for consistent internal representation.
        if self._signal.ndim == 1:
            self._signal = self._signal[np.newaxis, :]

        # Validate signal size against x.
        if self._x.size > 0 and self._signal.shape[-1] != self._x.size:
            raise ValueError(
                f"The signal size ({self._signal.shape[-1]}) must match the "
                f"X-axis size ({self._x.size})."
            )

        y = self._data.get("y", np.array([]))
        monitor = self._data.get("monitor", np.array([]))

        self._y = y.astype(np.float64)
        self._monitor = monitor.astype(np.float64)

        # Validate monitor size against x.
        if monitor.size > 0 and monitor.size != self._x.size:
            raise ValueError(
                f"The monitor size ({monitor.size}) must match the "
                f"X-axis size ({self._x.size})."
            )

        # Reset processing arrays.
        self._indices = np.array([])
        self.outliers, self.medians = np.array([]), np.array([])

        # Only reindex if data is valid.
        if self._x.size > 0 and self._signal.size > 0:
            self.reindex()
        else:
            logger.warning(
                f"The x and signal arrays are empty for scan {self.label}. "
                "Skipping reindexing."
            )

    def reindex(self):
        """Reindex the scan data."""
        if self._x.size == 0:
            return
        if self._indices.size == 0:
            self._indices = np.argsort(self._x, kind="stable")
        self._x = self._x[self._indices]
        self._signal = self._signal[:, self._indices]
        if self._monitor.size != 0:
            self._monitor = self._monitor[self._indices]

    @staticmethod
    def read_data_at_paths(
        filename: str, index: int, data_paths: str | list[str]
    ) -> npt.NDArray[np.float64]:
        """Read and return data from the file.

        Args:
            filename: Path to the HDF5 file.
            index: Scan index in the file.
            data_paths: Single path or list of paths to read.

        Returns:
            numpy.ndarray: The data read from the file.
        """
        data_paths = [data_paths] if isinstance(data_paths, str) else data_paths

        kwargs: dict[str, Any] = {}
        if use_blissdata_api:
            kwargs["retry_timeout"] = Config().get("dynamic_hdf5_retry_timeout")

        data: list[Any] = []
        with File(filename, **kwargs) as fh:
            if use_blissdata_api:
                # Always wait for the end of the scan if using Blissdata API; do not
                # remove this line.
                try:
                    _ = fh[f"{index}.1/end_time"]
                except Exception as e:
                    raise RuntimeError(
                        f"Error accessing data from scan {filename}::/{index}.1."
                    ) from e

            for data_path in data_paths:
                full_data_path = f"{index}{data_path}"

                try:
                    data_at_path = fh[full_data_path][()]  # type: ignore
                except KeyError as e:
                    raise KeyError(
                        f"Unable to access {filename}::/{full_data_path}."
                    ) from e
                except TypeError as e:
                    raise TypeError(
                        f"Unable to read data from {filename}::/{full_data_path}."
                    ) from e

                try:
                    data_at_path = np.asarray(data_at_path)  # type: ignore
                except ValueError as e:
                    raise ValueError(
                        f"Unable to convert data from {filename}::/{full_data_path} to "
                        "a Numpy array."
                    ) from e

                if data_at_path.size == 0:
                    raise ValueError(
                        f"Data from {filename}://{full_data_path} is empty."
                    )

                data.append(data_at_path)

        # Return the element of the array if it has only one element.
        if len(data) == 1:
            [data] = data

        return np.array(data)

    def find_outliers(self, method: str = "hampel", **kwargs: Any):
        """Find outliers in the signal.

        See the docstring in the :mod:`daxs.filters`.
        """
        if method == "hampel":
            self.outliers, self.medians = hampel(self._signal, axis=1, **kwargs)
        else:
            raise ValueError(f"Unknown outliers detection method {method}.")

    def remove_outliers(self, method: str = "hampel", **kwargs: Any):
        """Remove outliers from the signal.

        See the docstring of :meth:`daxs.scans.Scan.find_outliers`.
        """
        if self.outliers.size == 0 or self.medians.size == 0:
            self.find_outliers(method=method, **kwargs)

        if self.outliers.size > 0 and self.medians.size > 0:
            self._signal = np.where(self.outliers, self.medians, self._signal)
        else:
            logger.info("No outliers found for scan %s.", self.label)

    def dead_time_correction(
        self,
        tau: Iterable[float],
        detection_time: float | npt.NDArray[np.float64] | None = None,
    ):
        """Perform a dead time correction using a non-paralyzable model.

        Args:
            tau: The detector dead time in seconds.
            detection_time: The time spent on a point of the scan in seconds.
        """
        if detection_time is None:
            try:
                detection_time = copy.deepcopy(self._data["detection_time"])
            except KeyError:
                raise ValueError(
                    "Either the detection time parameter or `detection_time`"
                    " data path must be set."
                )
        else:
            detection_time = np.ones_like(self.signal) * detection_time

        detection_time = np.asarray(detection_time)

        if np.any(detection_time == 0):
            raise ValueError("The detection time has zero values.")

        tau = np.array(tau)
        if self._signal.shape[0] != tau.shape[0]:
            raise ValueError(
                "Each signal data path must have a detector dead time (tau) value."
            )

        norm = 1 - ((self._signal / detection_time).T * tau).T
        if np.any(norm == 0):
            raise ValueError("The normalization has zero values.")

        self._signal = self._signal / norm

    # TODO: Extract the interpolation logic to a separate class.
    def interpolate(self, a: npt.NDArray[np.float64]):
        """Interpolate the signal and monitor data to new X-axis values.

        Args:
            a: Array used to interpolate the signal and monitor.
        """
        if a.size == 0:
            raise ValueError("The new X-axis values must not be empty.")
        if self.signal.size == 0:
            raise ValueError("The signal values must not be empty.")

        logger.debug(
            "Interpolating the signal and monitor data for scan %s.", self.label
        )

        # The interpolated signal is probably going to have a different size,
        # so we can not change the values in-place, and a new array needs to be
        # initialized.
        signal = np.zeros((self._signal.shape[0], a.size))

        # Interpolate the signal from each counter individually.
        for i, _ in enumerate(self._signal):
            signal[i, :] = np.interp(
                a, self._x, self._signal[i, :], left=np.nan, right=np.nan
            )

        # Interpolate the monitor if present.
        if self._monitor.size > 0:
            self._monitor = np.interp(
                a, self._x, self._monitor, left=np.nan, right=np.nan
            )

        self._x = a
        self._signal = signal
        self._indices = np.array([])

        # Ensure indices are updated after interpolation
        self.reindex()

    def divide_by_scalars(
        self, signal_divisor: int | float, monitor_divisor: int | float | None = None
    ) -> Scan:
        """Divide the scan by scalar values."""
        if signal_divisor == 0:
            raise ValueError("Cannot divide by zero for signal.")
        self._signal /= signal_divisor
        if monitor_divisor is not None:
            if monitor_divisor == 0:
                raise ValueError("Cannot divide by zero for monitor.")
            self._monitor /= monitor_divisor
        return self

    def divide_by_scan(self, other: Scan) -> Scan:
        return self.__truediv__(other)

    def __truediv__(self, other: Scan) -> Scan:
        """Divide the scan by another scan."""
        # Check for empty or all-zero divisors before division.
        if other._signal.size == 0:
            raise ValueError("Cannot divide by empty signal.")
        if np.all(other._signal == 0):
            raise ValueError("Cannot divide by signal with all zero values.")

        try:
            self._signal /= np.nan_to_num(other._signal, nan=1)
        except ValueError as e:
            raise ValueError(
                "The signal arrays of the two scans must have the same shape."
            ) from e

        # Check for invalid values after division.
        if np.any(np.isinf(self._signal)):
            raise ValueError("Division resulted in infinite values in signal.")

        if self._monitor.size > 0 and other._monitor.size > 0:
            if np.all(other._monitor == 0):
                logger.warning(
                    "Monitor values are all zero. This may result in invalid data."
                )
            try:
                self._monitor /= np.nan_to_num(other._monitor, nan=1)
            except ValueError as e:
                raise ValueError(
                    "The monitor arrays of the two scans must have the same shape."
                ) from e

            # Check for invalid values in monitor after division.
            if np.any(np.isinf(self._monitor)):
                raise ValueError("Division resulted in infinite values in monitor.")

        return self

    def plot(self, axes: Axes | None = None, shift: float = 0.0, **kwargs: Any) -> Axes:
        """Plot the scan data and outliers if available.

        Args:
            axes: The axes to plot the scan data on.
            shift: Shift the signal by the given value.
            **kwargs: Additional keyword arguments passed to the plot function.

        Returns:
            The axes with the plotted scan data.

        Raises:
            ValueError: If the signal is empty.
        """
        if self._signal.size == 0:
            raise ValueError("Cannot plot empty signal.")

        FIGURE_SIZE = (6, 3.7)

        if axes is None:
            _, axes = plt.subplots(1, 1, figsize=FIGURE_SIZE)

        shift = float(np.nanmean(self._signal))
        for i, _ in enumerate(self._signal):
            axes.plot(self.x, self._signal[i, :] + i * shift, label=f"{i}")
            if self.outliers.size > 0:
                indices = self.outliers[i, :]
                axes.plot(
                    self.x[indices], self._signal[i, :][indices] + i * shift, "k."
                )
            axes.legend()
        return axes

    def __str__(self):
        return self.label


class Scans:
    """A collection of scans."""

    def __init__(self, scans: Scan | list[Scan] | None = None) -> None:
        """Initialize the collection of scans."""
        if scans is None:
            self.scans = []
        elif isinstance(scans, list):
            self.scans = scans
        else:
            self.scans = [scans]

    def check_sizes(self) -> None:
        """Sanity check for the number of points in the scans."""
        sizes = [scan.x.size for scan in self.scans]
        mean = np.mean(sizes)
        std = np.std(sizes)

        if any(abs(size - mean) > std for size in sizes):
            logger.warning(
                "The number of points in the selected scans have a "
                "large spread (mean = %.2f, standard deviation: %.2f).",
                mean,
                std,
            )

    def get_common_axis(
        self, label: str = "x", mode: str = "intersection"
    ) -> npt.NDArray[np.float64]:
        """Return the common axis for the scans."""
        if not self.scans:
            raise ValueError("There are no scans available.")

        def step(axis: npt.NDArray[np.float64]) -> float:
            return np.abs((axis[0] - axis[-1]) / (axis.size - 1))

        # If there is a single scan, use its axis as the common axis.
        if len(self.scans) == 1:
            [axis] = self.scans
            return getattr(axis, label)

        axes = sorted([getattr(scan, label) for scan in self.scans], key=np.min)

        # Initialize the common axis as the first axis.
        common_axis = axes[0]
        for i, axis in enumerate(axes):
            message = (
                f"{label.upper()}-axis parameters for scan {self.scans[i].label}: "
                f"start = {axis[0]:.8f}, stop = {axis[-1]:.8f}, "
                f"size = {axis.size:d}, step = {step(axis):.8f}."
            )
            logger.debug(message)

            if np.array_equal(common_axis, axis):
                continue

            common_axis = arrays.merge(common_axis, axis, mode=mode)

            if common_axis.size == 0 and mode == "intersection":
                message = (
                    f"The common {label.upper()}-axis is empty after merging scan "
                    f"{self.scans[i].label}. "
                    "Switching to union mode for the common axis search."
                )
                logger.warning(message)
                return self.get_common_axis(label, mode="union")

        message = (
            f"Common {label.upper()}-axis parameters using {mode} mode: "
            f"start = {common_axis[0]:.8f}, stop = {common_axis[-1]:.8f}, "
            f"size = {common_axis.size:d}, step = {step(common_axis):.8f}."
        )
        logger.info(message)

        return common_axis

    def reset(self) -> None:
        """Reset the scans to their original values."""
        for scan in self.scans:
            scan.reset()

    def extend(self, scans: Scans) -> None:
        """Extend the collection of scans."""
        self.scans.extend(scans)

    def __len__(self) -> int:
        """Return the number of scans in the collection."""
        return len(self.scans)

    def __iter__(self):
        """Iterate over the scans."""
        return iter(self.scans)

    def __getitem__(self, index: int) -> Scan:
        """Return the scan at the given index."""
        return self.scans[index]

    def remove(self, item: Scan) -> None:
        """Remove the scan at the given index."""
        self.scans.remove(item)

    def append(self, item: Scan) -> None:
        """Append a scan to the collection."""
        self.scans.append(item)
