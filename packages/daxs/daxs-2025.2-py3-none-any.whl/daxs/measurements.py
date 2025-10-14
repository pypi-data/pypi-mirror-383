"""The module provides classes to deal with different types of measurements."""

from __future__ import annotations

import contextlib
import copy
import logging
import os
from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Iterable

if TYPE_CHECKING:
    from matplotlib.axes import Axes

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt

from daxs import __version__ as version
from daxs.correctors import (
    DataDrivenConcentrationCorrector,
    SimpleConcentrationCorrector,
)
from daxs.interpolators import Interpolator2D
from daxs.scans import Scan, Scans
from daxs.sources import Source
from daxs.utils.arrays import trapezoid

logger = logging.getLogger(__name__)


class Measurement:
    """Base class for measurements."""

    def __init__(self, sources: Source | list[Source]):
        """Initialize the measurement.

        Args:
            sources: Sources of scans.
        """
        self.sources = [sources] if isinstance(sources, Source) else sources

        self._scans: Scans | None = None
        self._x: npt.NDArray[np.float64] = np.array([])
        self._signal: npt.NDArray[np.float64] = np.array([])
        self._monitor: npt.NDArray[np.float64] = np.array([])

    @property
    def x(self):
        if self._x.size == 0:
            self.process()
        return self._x

    @property
    def signal(self):
        if self._signal.size == 0:
            self.process()
        return self._signal

    @property
    def monitor(self):
        if self._monitor.size == 0:
            self.process()
        return self._monitor

    @property
    def scans(self) -> Scans:
        """The scans of the measurement."""
        if self._scans is None:
            self._scans = Scans()
            for source in self.sources:
                self._scans.extend(source.scans)

            if len(self._scans) == 0:
                raise ValueError("The measurement has no scans.")

            self._scans.check_sizes()

            self._x = np.array([])
            self._signal = np.array([])
            self._monitor = np.array([])
        return self._scans

    @abstractmethod
    def process(self, *args: Any, **kwargs: Any) -> None:
        """Process the scans data."""

    @abstractmethod
    def plot(self, axes: Any | None = None, **kwargs: Any) -> Any:
        """Plot the measurement signal.

        Args:
            axes: Matplotlib axes where to plot the signal.
            **kwargs: Additional arguments passed to the plot function.

        Returns:
            The matplotlib axes where the signal was plotted.
        """

    @abstractmethod
    def save(self, filename: str, delimiter: str = ",") -> None:
        """Save the current measurement data to a file.

        Args:
            filename: Name of the output file.
            delimiter: Column delimiter in the output file.
        """

    def add_source(self, source: Source) -> None:
        """Add a new source to the measurement.

        Args:
            source: Source to be added.
        """
        self.sources.append(source)
        self._scans = None

    def remove_source(self, index: int) -> None:
        """Remove a source from the measurement.

        Args:
            index: Index of the source to be removed.
        """
        self.sources.pop(index)
        self._scans = None

    def add_scans(self, scans: Scan | list[Scan]) -> None:
        """Add scans to the measurement.

        Args:
            scans: Scans to be added.
        """
        scans = [scans] if isinstance(scans, Scan) else scans

        if self._scans is None:
            self._scans = Scans()

        for scan in scans:
            self._scans.append(scan)
            logger.debug("Scan %s was added.", scan.label)

    def remove_scans(
        self, indices: int | list[int], filename: str | None = None
    ) -> None:
        """Remove scans from the measurement.

        Args:
            indices: Indices of the scans to be removed.
            filename: Name of the file from which the scans where read.
        """
        indices = [indices] if isinstance(indices, int) else indices

        for index in indices:
            for scan in self.scans:
                if index == scan.index and (
                    filename is None or scan.filename == filename
                ):
                    self.scans.remove(scan)
                    logger.debug("Scan %s was removed.", scan.label)

    def reset(self, scans: float = True):
        """Reset the measurement."""
        self._x, self._signal, self._monitor = np.array([]), np.array([]), np.array([])
        if scans:
            self.scans.reset()

    def get_scans(
        self, indices: int | list[int], filename: str | None = None
    ) -> list[Scan]:
        indices = [indices] if isinstance(indices, int) else indices

        scans = []
        for index in indices:
            for scan in self.scans:
                if scan.index == index and (
                    filename is None or scan.filename == filename
                ):
                    scans.append(scan)

        return scans

    def find_outliers(self, method: str = "hampel", **kwargs: Any):
        """Find outliers in the data.

        Note:
            See the docstring of :meth:`.scans.Scan.find_outliers` for details.
        """
        for scan in self.scans:
            scan.find_outliers(method=method, **kwargs)

    def remove_outliers(self, method: str = "hampel", **kwargs: Any):
        """Remove outliers from the signal.

        Note:
            See the docstring of :meth:`.scans.Scan.remove_outliers` for details.
        """
        logger.info("Removing outliers.")
        for scan in self.scans:
            scan.remove_outliers(method=method, **kwargs)
        self._signal = np.array([])

    def dead_time_correction(
        self,
        tau: Iterable[float],
        detection_time: float | npt.NDArray[np.float64] | None = None,
    ):
        """Perform a dead time correction using a non-paralyzable model.

        Args:
            tau: Dead time value(s).
            detection_time: Detection time value(s).

        Note:
            See the docstring of :meth:`.scans.Scan.dead_time_correction` for details.
        """
        for scan in self.scans:
            scan.dead_time_correction(tau, detection_time)

    def concentration_correction(
        self,
        indices: int | list[int] | npt.NDArray[np.int64] | None = None,
        data_mappings: dict[str, str] | None = None,
        scans: Scan | list[Scan] | Scans | None = None,
    ) -> None:
        """Apply the concentration correction using data from the specified scans.

        Args:
            indices: Indices of the scans used for concentration correction.
            data_mappings: Data mappings for the concentration correction scans.
            scans: Scans used for concentration corrections.

        Raises:
            ValueError: If neither indices nor scans are specified.
        """
        if indices is None and scans is None:
            raise ValueError("Either the indices or scans must be specified.")

        # Get the concentration correction scans.
        if indices is not None:
            indices = [indices] if isinstance(indices, int) else indices

            if len(self.sources) > 1:
                logger.warning(
                    "Using the first source for concentration correction scans. "
                    "Provide scan objects directly if correction scans are "
                    "from another source."
                )

            conc_corr_source = copy.deepcopy(self.sources[0])
            conc_corr_data_mappings = copy.deepcopy(conc_corr_source.data_mappings)

            # Update the data mappings if provided.
            if data_mappings is not None:
                conc_corr_data_mappings.update(data_mappings)

            # Try to set X-axis to elapsed_time.
            with contextlib.suppress(KeyError):
                conc_corr_data_mappings["x"] = ".1/measurement/elapsed_time"
                logger.debug(
                    "The X-axis mapping for the concentration "
                    "correction scans was updated to elapsed_time."
                )

            conc_corr_source.data_mappings = conc_corr_data_mappings
            conc_corr_scans = conc_corr_source.read_scans(indices)
        else:
            conc_corr_scans = scans if isinstance(scans, Scans) else Scans(scans)

        # Filter out x, y, signal, and monitor.
        if data_mappings is not None:
            for key in list(data_mappings.keys()):
                if key in ("x", "y", "signal", "monitor"):
                    del data_mappings[key]

        # Create and apply the appropriate corrector.
        if not data_mappings:
            corrector = SimpleConcentrationCorrector(conc_corr_scans)
        else:
            corrector = DataDrivenConcentrationCorrector(conc_corr_scans, data_mappings)

        corrector.apply(self.scans)

        # Force reevaluation of signal and monitor.
        self._signal, self._monitor = np.array([]), np.array([])


class Measurement1D(Measurement):
    """Base class for 1D measurements."""

    @property
    def x(self):
        if self._x.size == 0:
            self._x = self.scans.get_common_axis()
            # Assign the common axis to the scans.
            for scan in self.scans:
                scan.x = self._x
        return self._x

    @x.setter
    def x(self, a: npt.NDArray[np.float64]):
        logger.info("Setting new X-axis.")
        for scan in self.scans:
            scan.x = a
        self._x = a
        self._signal, self._monitor = np.array([]), np.array([])

    def process(
        self, aggregation: str = "fraction of sums", normalization: str | None = None
    ):
        """Process the scans data.

        Args:
            aggregation: Method to use for aggregating data.
            normalization: Method to use for normalizing the signal.

        Note:
            The processing includes aggregating the data of the selected scans
            and normalizing the signal.
        """
        self.aggregate(mode=aggregation)
        if normalization is not None:
            self.normalize(mode=normalization)

    def aggregate(self, mode: str = "fraction of sums"):
        """Aggregate the scans signal using the selected mode.

        Args:
            mode: Defines how the signal is aggregated.

                - "fraction of sums": fraction of the signals sum and monitors sum
                - "mean of fractions", mean of the signal and monitor fractions

        Raises:
            ValueError: If the aggregation mode is unknown.

        Note:
            When present, the aggregated monitor is always a mean of the monitors from
            the individual scans.
        """
        if mode not in ("fraction of sums", "mean of fractions"):
            raise ValueError(f"Unknown aggregation mode {mode}.")

        self._signal = np.zeros_like(self.x)
        self._monitor = np.zeros_like(self.x)

        for scan in self.scans:
            signal = np.nan_to_num(scan.signal, nan=0)
            monitor = np.nan_to_num(scan.monitor, nan=0)

            if mode == "fraction of sums" or monitor.size == 0:
                self._signal += signal
            elif mode == "mean of fractions":
                # Increment the signal by the fraction signal/monitor, and handle
                # division by zero by setting the result to NaN for those points.
                self._signal += np.divide(
                    signal,
                    monitor,
                    out=np.full_like(signal, np.nan),
                    where=monitor != 0,
                )

            # Increment the monitor if it is a non-empty array.
            if monitor.size != 0:
                self._monitor += monitor

        if mode == "fraction of sums":
            # If the monitor is all zeros, divide the signal by the number of scans.
            if np.all(self._monitor == 0):
                self._signal = self._signal / len(self.scans)
            else:
                self._signal = np.divide(
                    self._signal,
                    self._monitor,
                    out=np.full_like(self._signal, np.nan),
                    where=self._monitor != 0,
                )
        elif mode == "mean of fractions":
            self._signal = self._signal / len(self.scans)

        # The monitor is always a mean of the monitors from the individual scans.
        self._monitor = self._monitor / len(self.scans)

        if np.all(self._monitor == 0):
            self._monitor = np.array([])

        logger.info(f"The scans data was aggregated using the {mode} mode.")

    def normalize(self, mode: str = "area") -> None:
        """Normalize the signal.

        Args:
            mode: Defines how the signal is normalized.

                - "area": Normalize using the absolute signal area calculated using the
                  trapezoidal rule.
                - "maximum": Normalize using the absolute maximum intensity of the
                  signal.

        Raises:
            ValueError: If the normalization mode is unknown.

        Note:
            This will overwrite the original signal with the normalized one.
        """
        if self._signal.size == 0:
            self.aggregate()

        if mode == "area":
            self._signal = self._signal / np.abs(trapezoid(self._signal, self.x))
        elif mode == "maximum":
            self._signal = self._signal / np.abs(np.nanmax(self._signal))
        else:
            raise ValueError(f"Unknown normalization mode {mode}.")

        logger.info("The signal was normalized using the %s.", mode)

    def plot(self, axes: Axes | None = None, **kwargs: Any) -> Axes:
        """Plot the measurement signal.

        Args:
            axes: Matplotlib axes where to plot the signal.
            **kwargs: Additional arguments passed to the plot function.

        Returns:
            The matplotlib axes where the signal was plotted.

        Raises:
            ValueError: If the signal is not defined.
        """
        if self.signal.size == 0:
            raise ValueError("The signal is not defined.")

        if axes is None:
            FIGURE_SIZE = (6, 3.7)
            fig = plt.figure(figsize=FIGURE_SIZE)
            axes = fig.subplots(1, 1)

        axes.plot(self.x, self.signal, **kwargs)

        fig = axes.get_figure()
        if fig is not None:
            fig.tight_layout()

        return axes

    def save(self, filename: str, delimiter: str = ",") -> None:
        """Save the current measurement data to a file.

        Args:
            filename: Name of the output file.
            delimiter: Column delimiter in the output file.

        Raises:
            ValueError: If the signal is not defined.
        """
        if self.signal.size == 0:
            raise ValueError("The signal is not defined.")

        with open(filename, "w", encoding="utf-8") as fp:
            fp.write(f"# Data saved from daxs version {version}\n")

            if self.monitor.size > 0:
                fp.write(
                    "# Columns: x mean_signal mean_signal_no_monitor mean_monitor\n"
                )
                mean_signal_raw = self.signal * self.monitor / len(self.scans)
                data = np.stack(
                    (self.x, self.signal, mean_signal_raw, self.monitor), axis=1
                )
                np.savetxt(fp, data, delimiter=delimiter, fmt="%.6e %.6e %.6e %.6e")
            else:
                fp.write("# Columns: x mean_signal\n")
                data = np.stack((self.x, self.signal), axis=1)
                np.savetxt(fp, data, delimiter=delimiter, fmt="%.6e %.6e")

            logger.info("The data was saved to %s.", filename)


class Xas(Measurement1D):
    """Class to represent a X-ray absorption measurement."""


class Xes(Measurement1D):
    """Class to represent a X-ray emission measurement."""


class Measurement2D(Measurement):
    """Base class for 2D measurements."""

    def __init__(self, sources: Source | list[Source]):
        super().__init__(sources=sources)
        self._y: npt.NDArray[np.float64] = np.array([])
        self._interpolator: Interpolator2D | None = None
        self._shape: tuple[int, int] | None = None
        self.cuts = {}

    @property
    def y(self):
        if self._y.size == 0:
            self.process()
        return self._y

    @property
    def shape(self) -> tuple[int, int]:
        """Shape of the current plane."""
        if self._shape is None:
            self.process()
        if self._shape is None:
            raise ValueError("The shape is not defined.")
        return self._shape

    @shape.setter
    def shape(self, value: tuple[int, int]):
        """Set the shape of the current plane.

        Args:
            value: Shape of the current plane as (nx, ny).
        """
        if value[0] * value[1] != self.signal.size:
            raise ValueError("The shape is incompatible with the signal size.")
        self._shape = value

    @property
    def interpolator(self):
        """The interpolator of the current plane."""
        if self._interpolator is None:
            self._interpolator = Interpolator2D(self.x, self.y, self.signal)
        return self._interpolator

    def reset(self, scans: float = True):
        """Reset the measurement."""
        super().reset(scans=scans)
        self._y = np.array([])
        self.cuts = {}
        self._interpolator = None

    def concentration_correction(
        self,
        indices: int | list[int] | None | npt.NDArray[np.int64] = None,
        data_mappings: dict[str, str] | None = None,
        scans: Scan | list[Scan] | Scans | None = None,
    ) -> None:
        super().concentration_correction(indices, data_mappings, scans)
        self._y = np.array([])
        self._interpolator = None

    def interpolate(self, xi: npt.NDArray[np.float64], yi: npt.NDArray[np.float64], /):
        """Interpolate the plane using the new axes.

        A regular grid defined by the new axes is used to interpolate the signal.
        The current x, y, and shape are also updated with the new values.

        Args:
            xi: The new X-axis.
            yi: The new Y-axis.
        """
        x, y = np.meshgrid(xi, yi)
        x = x.ravel()
        y = y.ravel()
        points = np.stack((x, y), axis=-1)
        signal = self.interpolator(points)

        # Flatten array.
        signal = signal.ravel()

        # Assign the values.
        self._x, self._y, self._signal = x, y, signal
        self._shape = (xi.size, yi.size)

        # Update the interpolator.
        self.interpolator.update({"x": x, "y": y, "z": signal})

    def cut(
        self,
        mode: str = "CEE",
        energies: list[float] | None = None,
        widths: float | list[float] | None = None,
        nbins: int | None = None,
    ):
        """Calculate the cuts specified by the mode and energies.

        Args:
            mode: Defines the way to cut the plane:

                - "CEE" - constant emission energy
                - "CIE" - constant incident energy
                - "CET" - constant energy transfer

            energies: List of energy values at which to extract cuts. Units should
                match the data axes.
            widths: Widths of the energy window for each cut, centered at the specified
                energy. If None, if defaults to the approximate distance between the
                points along the relevant axis. Units should match the data axes.
            nbins: Number of bins used to histogram the cut data. Using too
                many bins may result in empty bins with NaN values.

        Returns:
            Dictionary with the cuts. Each entry has the form
            `"{mode}@{energy}": (centers, signal, mask)`, where `centers` are the
            centers of the bins, `signal` is the signal of the cut, and `mask` is a
            boolean array indicating which data points were included in the cut.

        Raises:
            ValueError: If the energies parameter is not defined or if the mode is
                unknown.
        """
        if energies is None:
            raise ValueError("The energies parameter must be defined.")

        mode = mode.upper()
        if mode not in ("CIE", "CEE", "CET"):
            raise ValueError(f"Unknown mode {mode}.")

        x_dim, y_dim = self.shape
        x_range = self.x.max() - self.x.min()
        y_range = self.y.max() - self.y.min()

        if widths is None:
            widths = {
                "CIE": x_range / x_dim,
                "CEE": y_range / y_dim,
                "CET": (x_range + y_range) / (x_dim + y_dim),
            }[mode]

        logger.info(f"The cuts will use a width of {widths:.1e}.")

        if isinstance(widths, float):
            widths = [widths] * len(energies)

        if not isinstance(widths, list):
            raise ValueError(
                "The widths parameter must be a float or a list of floats."
            )

        # A reduction factor to avoid using too many bins and end up with empty ones.
        NBINS_REDUCTION_FACTOR = 0.9

        for energy, width in zip(energies, widths):
            energy_min = energy - width / 2
            energy_max = energy + width / 2

            if mode == "CIE":
                mask = (self.x >= energy_min) & (self.x <= energy_max)
                points = self.y[mask]
                nbins = int(y_dim * NBINS_REDUCTION_FACTOR)
            elif mode == "CEE":
                mask = (self.y >= energy_min) & (self.y <= energy_max)
                points = self.x[mask]
                nbins = int(x_dim * NBINS_REDUCTION_FACTOR)
            elif mode == "CET":
                mask = (self.x - self.y >= energy_min) & (self.x - self.y <= energy_max)
                points = self.x[mask]
                points_range = points.max() - points.min()
                nbins = int(points_range / x_range * x_dim * NBINS_REDUCTION_FACTOR)
            else:
                raise ValueError(f"Unknown mode {mode}.")

            logger.debug(f"Extracting {mode} cut at {energy} +/- {width / 2}.")
            logger.debug(f"Using {nbins} bins for the histogram.")

            signal = self.signal[mask]
            signal, edges = np.histogram(points, bins=nbins, weights=signal)
            centers = (edges[1:] + edges[:-1]) / 2.0
            counts, _ = np.histogram(points, bins=edges)

            signal = np.divide(
                signal,
                counts,
                out=np.full_like(signal, np.nan),
                where=counts != 0,
            )

            self.cuts[f"{mode}@{energy}"] = (centers, signal, mask)

    def plot(
        self, axes: npt.NDArray[Any] | None = None, **kwargs: Any
    ) -> npt.NDArray[Any]:
        """Plot the measurement signal.

        Args:
            axes: Matplotlib axes where to plot the signal.
            **kwargs: Additional arguments passed to the plot function.

        Returns:
            The matplotlib axes where the signal was plotted.

        Raises:
            ValueError: If the signal is not defined or if the axes are not provided or
                have an incorrect number of elements.
        """
        if "cmap" not in kwargs:
            kwargs["cmap"] = "viridis"

        if "levels" not in kwargs:
            kwargs["levels"] = 42

        if axes is None:
            FIGURE_SIZE = (5.56, 9)
            fig = plt.figure(figsize=FIGURE_SIZE)
            axes = fig.subplots(2, 1)

        if axes is None:
            raise ValueError("Axes must be provided for plotting.")

        EXPECTED_AXES_COUNT = 2
        if axes.size != EXPECTED_AXES_COUNT:
            raise ValueError("Two axes must be provided for plotting.")

        ax1, ax2 = axes.flatten()

        cs1 = ax1.tricontourf(self.x, self.y, self.signal, **kwargs)
        cs2 = ax2.tricontourf(self.x, self.x - self.y, self.signal, **kwargs)

        ax1.set_xlabel("Incident Energy")
        ax1.set_ylabel("Emission Energy")
        ax2.set_xlabel("Incident Energy")
        ax2.set_ylabel("Energy Transfer")

        fig = ax1.get_figure()
        fig.colorbar(cs1, ax=ax1)
        fig.colorbar(cs2, ax=ax2)

        fig.tight_layout()

        # Plot the cuts in separate 1D figures.
        for label, (centers, signal, mask) in self.cuts.items():
            ax1.scatter(self.x[mask], self.y[mask], s=0.5)
            ax2.scatter(self.x[mask], self.x[mask] - self.y[mask], s=0.5)

            # Get the color used in the previous plot.
            color = ax2.collections[-1].get_facecolor()[0]

            # Create a new figure for the cut if it does not exist.
            mode = label.split("@")[0]
            FIGURE_SIZE_CUTS = (6, 3.7)
            fig = plt.figure(mode, figsize=FIGURE_SIZE_CUTS)
            ax = fig.gca()
            ax.plot(centers, signal, label=label, color=color)
            if mode == "CIE":
                ax.set_xlabel("Emission Energy")
            elif mode in ("CEE", "CET"):
                ax.set_xlabel("Incident Energy")
            ax.set_ylabel("Signal")
            ax.legend()
            fig.tight_layout()
            # Append the axis to the list of 2D plot axes.
            axes.tolist().append(ax)

        return np.asarray(axes)

    def save(self, filename: str, delimiter: str = ",") -> None:
        """Save the current measurement data to a file.

        Args:
            filename: Name of the output file.
            delimiter: Column delimiter in the output file.

        Raises:
            ValueError: If the signal is not defined.
        """
        if self.signal.size == 0:
            raise ValueError("The signal is not defined.")

        with open(filename, "w", encoding="utf-8") as fp:
            fp.write(f"# Data saved from daxs version {version}\n")

            if self.monitor.size > 0:
                fp.write("# Columns: x y signal monitor\n")
                data = np.stack((self.x, self.y, self.signal, self.monitor), axis=1)
                np.savetxt(fp, data, delimiter=delimiter, fmt="%.6e %.6e %.6e %.6e")
            else:
                fp.write("# x y signal\n")
                data = np.stack((self.x, self.y, self.signal), axis=1)
                np.savetxt(fp, data, delimiter=delimiter, fmt="%.6e %.6e %.6e")

        logger.info("The data was saved to %s.", filename)

        # Save cuts to individual files if present.
        if self.cuts:
            base, ext = os.path.splitext(filename)
            for label, (centers, signal, _) in self.cuts.items():
                cut_filename = f"{base}_{label.replace('@', '_').lower()}{ext}"
                with open(cut_filename, "w", encoding="utf-8") as fp:
                    fp.write(f"# Data saved from daxs version {version}\n")
                    fp.write(f"# Cut: {label}\n")
                    fp.write("# Columns: energy signal\n")
                    data = np.stack((centers, signal), axis=1)
                    np.savetxt(fp, data, delimiter=delimiter, fmt="%.6e %.6e")
                logger.info("%s cut saved to %s.", label, cut_filename)


class Rixs(Measurement2D):
    """Class to represent a resonant inelastic X-ray scattering measurement."""

    @property
    def acquisition_mode(self):
        """Determine the acquisition mode of the RIXS plane.

        Returns:
            String indicating the acquisition mode ("absorption" or "emission").

        Note:
            There are two ways to measure a RIXS plane:

            1. Step through a range of emission energies and scan the incoming
            (monochromator) energy for each step.

            2. Step through incoming (monochromator) energy and scan the
            emission energy.

        """
        if all(scan.y is not None and scan.y.size == 1 for scan in self.scans):
            mode = "absorption"
        else:
            mode = "emission"
        logger.debug("The RIXS plane was acquired in %s mode.", mode)
        return mode

    def process(self):
        """Read and store the scans data."""
        acquisition_mode = self.acquisition_mode

        if acquisition_mode == "emission":
            raise NotImplementedError("The emission mode is not implemented yet.")

        if acquisition_mode == "absorption":
            for scan in self.scans:
                self._x = np.append(self._x, scan.x)
                self._y = np.append(self._y, scan.y * np.ones_like(scan.x))
                if scan.monitor.size == 0:
                    self._signal = np.append(self._signal, scan.signal)
                else:
                    # Append to the signal the fraction scan/monitor of the scan, and
                    # handle division by zero by setting the result to NaN for those
                    # points.
                    self._signal = np.append(
                        self._signal,
                        np.divide(
                            scan.signal,
                            scan.monitor,
                            out=np.full_like(scan.signal, np.nan),
                            where=scan.monitor != 0,
                        ),
                    )
                    self._monitor = np.append(self._monitor, scan.monitor)
            # The shape of the plane is (number of points per scan, number of scans).
            self._shape = (self._signal.size // len(self.scans), len(self.scans))
