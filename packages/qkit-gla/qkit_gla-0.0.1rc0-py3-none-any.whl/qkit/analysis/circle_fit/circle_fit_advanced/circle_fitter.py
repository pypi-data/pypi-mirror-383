#!/usr/bin/env python

"""Circuit analysis tools for superconducting resonator measurement data.

This module provides tools for analyzing the frequency response of superconducting
resonators using circle fitting methods. It extracts key parameters such as 
resonance frequency, quality factors, and delay corrections from complex scattering
data (S11 or S21).

The implementation is based on established methods from microwave engineering and
quantum circuit analysis, particularly useful for characterizing superconducting
quantum devices.

References:
    Probst, S., et al. "Efficient and robust analysis of complex scattering data
    under noise in microwave resonators." Review of Scientific Instruments 86.2 (2015).
    
    Rieger, M., et al. "Investigating Fano resonances and asymmetric line shapes
    in double-slit superconducting quantum interference devices." 
    arXiv preprint arXiv:2209.03036 (2022).

Example:
    >>> fitter = CircleFitter(frequencies, s21_data)
    >>> results = fitter.fit_result()
    >>> quality_factor = results["Qi"]
    >>> resonance_freq = results["fr"]

Attributes:
    plot_enable: Boolean flag indicating if plotting functionality is available.

    
@author: Wridhdhisom Karar ,2024

inspired by and based on resonator tools of Sebastian Probst
https://github.com/sebastianprobst/resonator_tools
"""

import logging

# from logging.config import _LoggerConfiguration
from typing import Optional

import numpy as np
import scipy.constants as const
import scipy.optimize as spopt
from scipy.ndimage.filters import gaussian_filter1d

# Import specific functions from helper_functions instead of using wildcard import
from .helper_functions import Watt2dBm, dBm2Watt

plot_enable = False
try:
    import qkit

    if qkit.module_available("matplotlib"):
        import matplotlib.pyplot as plt

        plot_enable = True
except (ImportError, AttributeError):
    try:
        import matplotlib.pyplot as plt

        plot_enable = True
    except ImportError:
        plot_enable = False


class CircleFitter:
    """Base class for common routines and definitions shared between both ports.

    This class provides methods to analyze complex scattering data using circle fitting
    techniques. It handles normalization, calibration, and extraction of quality factors
    and other resonator parameters.

    Attributes:
        n_ports: Number of ports (set by child classes).
        f_data: Array of frequency points.
        z_data_raw: Complex scattering data.
        fitresults: Dictionary containing the fit results.

    Note:
        This class is meant to be subclassed for specific port configurations.
    """

    # Will be overridden by subclasses for specific port configurations
    n_ports = 1

    def __init__(
        self,
        f_data: np.ndarray,
        z_data_raw: Optional[np.ndarray] = None,
        delay: Optional[float] = 0.0,
        power: float = 0,
    ):
        """Initialize the CircleFitter instance.

        Args:
            f_data: Array of frequency points in Hz where measurements were taken.
            z_data_raw: Complex scattering data (S11 or S21) corresponding to f_data.
            delay: Time delay between output and input signal leading to linearly
                frequency dependent phase shift, in seconds.
            power: Power level in dBm at which measurements were taken.
        """

        self.f_data = np.array(f_data)
        self.z_data_raw = np.array(z_data_raw) if z_data_raw is not None else None
        self.z_data_norm = None
        self.delay = delay
        self.fitresults = {}
        self.power = power
        self.fit_delay_max_iterations = 15

    @classmethod
    def Sij(cls, f, fr, Ql, Qc, phi=0.0, a=1.0, alpha=0.0, delay=0.0):
        """
        Full model for S11 of single-port reflection measurements or S21 of
        notch configuration measurements. The models only differ in a factor of
        2 which is set by the dedicated port classes inheriting from this class.

        inputs:
        - fr: Resonance frequency
        - Ql: Loaded quality factor
        - Qc: Coupling (aka external) quality factor. Calculated with
              diameter correction method, i.e. 1/Qc = Re{1/|Qc| * exp(i*phi)}
        - phi (opt.): Angle of the circle's rotation around the off-resonant
                      point due to impedance mismatches or Fano interference.
        - a, alpha (opt.): Arbitrary scaling and rotation of the circle w.r.t.
                           origin
        - delay (opt.): Time delay between output and input signal leading to
                        linearly frequency dependent phase shift
        """
        complexQc = Qc * np.cos(phi) * np.exp(-1j * phi)
        return (
            a
            * np.exp(1j * (alpha - 2 * np.pi * f * delay))
            * (
                1.0
                - 2.0
                * Ql
                / (complexQc * cls.n_ports * (1.0 + 2j * Ql * (f / fr - 1.0)))
            )
        )

    def fit_result(self, plot=False, prefit=None):
        """
        Returns the fit results as a dictionary.
        ## If plot is True, it will also plot the results twice.
        """
        print("delay in autofit", self.delay)
        self.autofit(fixed_delay=self.delay, prefit=None)
        if plot:
            self.plotall()
        return self.fitresults

    def autofit(self, calc_errors=True, fixed_delay=None, isolation=15, prefit=None):
        """
        Automatically calibrate data, normalize it and extract quality factors.
        If the autofit fails or the results look bad, please discuss with
        author.

        no need to pass delay if given during init,

        prefit, gets the fit results from the previous fit, and uses it as a guess for the current fit
        suitable for higher powers, where the Ql changes and the Qc changes, and the radius changes
        """
        if prefit is not None:
            # Use prefit results as initial guess for the fit and then update
            prefit["a"]
            prefit["alpha"]
            prefit["theta"]
            fr = prefit["fr"]
            Ql = prefit["Ql"]
            prefit["Qc"]
            delay = prefit["delay"]

            self.fitresults.update(prefit)
            self.delay = delay  # update delay from the prev fit
            guess = (fr, Ql, delay)
        else:
            guess = None

        if fixed_delay is None:
            pass
            # self._fit_delay() # TODO : fix the delay calculator.
        else:
            # Store result in dictionary (also for backwards-compatibility)            self.fitresults["delay"] = fixed_delay
            self.xc, self.yc, r0 = self._fit_circle(self.z_data_raw)
            self.fitresults["r0"] = r0
            self.fitresults["c"] = complex(self.xc, self.yc)
            self.z_data_raw - complex(self.xc, self.yc)
        # Find first estimate of parameters
        # fr, Ql, theta, self.delay_excess = self._fit_phase(z_data) # put this into auto delay calculation, no need TODO
        logging.info(
            f"the delay entered is {self.delay:.2e} ns, \n fitresults : {self.fitresults}"
        )

        # don't do anything with fixed_delay, calibrate uses the passes init delay. Or pass with prefit.
        self._calibrate(
            phase_guess=guess
        )  # finds all the parameters after phase fit, and delay fit ;6 parameters
        self._normalize()
        self._extract_Qs(calc_errors=calc_errors)
        self.calc_fano_range(isolation=isolation)

        # Prepare model data for plotting
        self.z_data_sim = self.Sij(
            self.f_data,
            self.fr,
            self.Ql,
            self.Qc,
            self.phi,
            self.a,
            self.alpha,
            self.delay,
        )
        self.z_data_sim_norm = self.Sij(
            self.f_data, self.fr, self.Ql, self.Qc, self.phi
        )

        photons = self.get_photons_in_resonator(power=self.power, diacorr=False)
        single_photon_power = self.get_single_photon_limit(diacorr=False)

        self.fitresults.update(
            {
                "sigma": self.sigma,
                "photons": photons,
                "single_photon_power": single_photon_power,
            }
        )

    def _fit_delay(self):
        """Finds the cable delay by repeatedly centering the "circle" and fitting
        the slope of the phase response.

        This method iteratively improves the estimation of the cable delay between
        the input and output signals, which causes a linearly frequency-dependent phase shift.
        """

        # Translate data to origin
        xc, yc, r0 = self._fit_circle(self.z_data_raw)
        z_data = self.z_data_raw - complex(xc, yc)
        # Find first estimate of parameters
        fr, Ql, theta, self.delay = self._fit_phase(z_data)

        # Do not overreact (see end of for loop)
        self.delay *= 0.05

        # Iterate to improve result for delay
        for i in range(self.fit_delay_max_iterations):
            # Translate new best fit data to origin
            z_data = self.z_data_raw * np.exp(2j * np.pi * self.delay * self.f_data)
            xc, yc, r0 = self._fit_circle(z_data)
            z_data -= np.complex(xc, yc)

            # Find correction to current delay
            guesses = (fr, Ql, 5e-11)
            fr, Ql, theta, delay_corr = self._fit_phase(z_data, guesses)

            # Stop if correction would be smaller than "measurable"
            phase_fit = self.phase_centered(self.f_data, fr, Ql, theta, delay_corr)
            residuals = np.unwrap(np.angle(z_data)) - phase_fit
            if 2 * np.pi * (self.f_data[-1] - self.f_data[0]) * delay_corr <= np.std(
                residuals
            ):
                break

            # Avoid overcorrection that makes procedure switch between positive
            # and negative delays
            if delay_corr * self.delay < 0:  # different sign -> be careful
                if abs(delay_corr) > abs(self.delay):
                    self.delay *= 0.5
                else:
                    # delay += 0.1*delay_corr
                    self.delay += 0.1 * np.sign(delay_corr) * 5e-11
            else:  # same direction -> can converge faster
                if abs(delay_corr) >= 1e-8:
                    self.delay += min(delay_corr, self.delay)
                elif abs(delay_corr) >= 1e-9:
                    self.delay *= 1.1
                else:
                    self.delay += delay_corr

        if 2 * np.pi * (self.f_data[-1] - self.f_data[0]) * delay_corr > np.std(
            residuals
        ):
            logging.warning("Delay could not be fit properly!")

        # Store result in dictionary (also for backwards-compatibility)
        self.fitresults["delay"] = self.delay

    def _SNR(self, data, r=None, c=[0, 0]):
        """
        calculates the SNR of the resonator
        when the data is centered
        """
        if r is None:
            r = np.mean(data)
        dist = abs(data - (c[0] + 1j * c[1]))
        self.sigma = np.std(dist - r, ddof=1)
        return np.abs(r) / self.sigma

    def _calibrate(self, phase_guess: Optional[tuple[float, float, float]] = None):
        """Finds the parameters for normalization of the scattering data.

        This method calibrates the raw data by correcting for delay and calculating
        various parameters needed for the circle fit analysis.

        Args:
            phase_guess: Optional initial guess for parameters (fr, Ql, delay) passed
                from previous fits, useful for higher powers.
        """

        # Correct for delay and translate circle to origin
        delay = 0.0 if self.delay is None else self.delay
        z_data = self.z_data_raw * np.exp(2j * np.pi * delay * self.f_data)

        self.z_data_corr = z_data.copy()  # store the corrected data
        # z_data_smooth=soft_averager(z_data.real,2)+(1j*soft_averager(z_data.imag,2))

        # Plot delay calibration if logging level is set to INFO or lower
        if logging.getLogger().getEffectiveLevel() <= logging.INFO:
            plt.figure()
            plt.scatter(np.real(self.z_data_raw), np.imag(self.z_data_raw))
            plt.scatter(np.real(z_data), np.imag(z_data))
            plt.gca().set_aspect("equal", adjustable="box")
            plt.title("Raw data delay calibrated")
            plt.show()

        # Hence the data should be delay corrected to fit the circle
        xc, yc, r0 = self._fit_circle(z_data)

        # xc, yc, r0 = self._fit_circle(z_data_smooth)
        zc = np.complex(xc, yc)
        z_data -= zc  # shift to the center
        # Find off-resonant point by fitting offset phase
        # (centered circle corresponds to lossless resonator in reflection)
        # fr, Ql, theta, self.delay_remaining HAVE TO BE FIT  for all powers, we can see how Ql changes --> changes the Qc, and radius

        self.fr, self.Ql, theta, self.delay_remaining = self._fit_phase(
            z_data, phase_guess
        )
        self.theta = self._periodic_boundary(theta)
        beta = self._periodic_boundary(self.theta - np.pi)
        offrespoint = zc + r0 * np.cos(beta) + 1j * r0 * np.sin(beta)
        self.offrespoint = offrespoint
        self.a = np.abs(offrespoint)
        self.alpha = np.angle(offrespoint)
        self.phi = self._periodic_boundary(beta - self.alpha)
        self.SNR = self._SNR(z_data, r=r0)

        # Store radius for later calculation
        self.r0 = r0 / self.a

        # Store results in dictionary (also for backwards-compatibility)
        self.fitresults.update(
            {
                "c": zc,
                "r0": r0,
                "r0_norm": self.r0,
                "delay_remaining": self.delay_remaining,  # delay after manual delay from phase fit
                "a": self.a,
                "alpha": self.alpha,  # ang_a
                "theta": self.theta,  # beta=theta0 -pi
                "phi": self.phi,  # impeadance coupling mismatch ; beta- alpha
                "fr": self.fr,
                "Ql": self.Ql,
                "SNR": self.SNR,
            }
        )

    def _normalize(self):
        """
        Transforms scattering data into canonical position with off-resonant
        point at (1, 0) (does not correct for rotation phi of circle around
        off-resonant point).
        """
        self.z_data_norm = (
            self.z_data_raw
            / self.a
            * np.exp(1j * (-self.alpha + 2.0 * np.pi * self.delay * self.f_data))
        )

    def _extract_Qs(self, refine_results=False, calc_errors=True):
        """
        Calculates Qc and Qi from radius of circle. All needed info is known
        already from the calibration procedure.
        """

        self.absQc = self.Ql / (self.n_ports * self.r0)
        # For Qc, take real part of 1/(complex Qc) (diameter correction method)
        if self.absQc > self.Ql:
            logging.warning(
                "Calculated Qc is larger than loaded Q! This is unphysical. Qi will be negative !"
            )
        self.Qc = self.absQc / np.cos(self.phi)
        self.Qi = 1.0 / (1.0 / self.Ql - 1.0 / self.Qc)
        self.Qi_no_dia_corr = 1.0 / (1.0 / self.Ql - 1.0 / self.absQc)

        # Store results in dictionary (also for backwards-compatibility)
        self.fitresults.update(
            {
                "fr": self.fr,
                "Ql": self.Ql,
                "Qc": self.Qc,
                "Qc_abs": self.absQc,
                "Qi": self.Qi,
                "Qi_no_dia_corr": self.Qi_no_dia_corr,
            }
        )

        # Calculate errors if wanted, later TODO
        if calc_errors:
            chi_square, cov = self._get_covariance()

            if cov is not None:
                fr_err, Ql_err, absQc_err, phi_err = np.sqrt(np.diag(cov))
                # Calculate error of Qi with error propagation
                # without diameter correction
                dQl = 1.0 / ((1.0 / self.Ql - 1.0 / self.absQc) * self.Ql) ** 2
                dabsQc = -1.0 / ((1.0 / self.Ql - 1.0 / self.absQc) * self.absQc) ** 2
                Qi_no_dia_corr_err = np.sqrt(
                    dQl**2 * cov[1][1]
                    + dabsQc**2 * cov[2][2]
                    + 2.0 * dQl * dabsQc * cov[1][2]
                )
                # with diameter correction
                dQl = 1.0 / ((1.0 / self.Ql - 1.0 / self.Qc) * self.Ql) ** 2
                dabsQc = (
                    -np.cos(self.phi)
                    / ((1.0 / self.Ql - 1.0 / self.Qc) * self.absQc) ** 2
                )
                dphi = -np.sin(self.phi) / (
                    (1.0 / self.Ql - 1.0 / self.Qc) ** 2 * self.absQc
                )
                Qi_err = np.sqrt(
                    dQl**2 * cov[1][1]
                    + dabsQc**2 * cov[2][2]
                    + dphi**2 * cov[3][3]
                    + 2
                    * (
                        dQl * dabsQc * cov[1][2]
                        + dQl * dphi * cov[1][3]
                        + dabsQc * dphi * cov[2][3]
                    )
                )
                self.fitresults.update(
                    {
                        "fr_err": fr_err,
                        "Ql_err": Ql_err,
                        "absQc_err": absQc_err,
                        "phi_err": phi_err,
                        "Qi_err": Qi_err,
                        "Qi_no_dia_corr_err": Qi_no_dia_corr_err,
                        "chi_square": chi_square,
                    }
                )
            else:
                logging.warning("Error calculation failed!")
        else:
            # Just calculate reduced chi square (4 fit parameters reduce degrees
            # of freedom)
            self.fitresults["chi_square"] = (
                1.0
                / (len(self.f_data) - 4.0)
                * np.sum(np.abs(self._get_residuals_reflection) ** 2)
            )

    def calc_fano_range(self, isolation=15, b=None):
        """
        Calculates the systematic Qi (and Qc) uncertainty range based on
        Fano interference with given strength of the background path
        (cf. Rieger & Guenzler et al., arXiv:2209.03036).

        inputs: either of
        - isolation (dB): Suppression of the interference path by this value.
                          The corresponding relative background amplitude b
                          is calculated with b = 10**(-isolation/20).
        - b (lin): Relative background path amplitude of Fano. Uppper limit can be max=(b. sin (psi))
        which is the imaginary point where the off. res point lies after delay correction + normalization.

        outputs (added to fitresults dictionary):
        - Qi_min, Qi_max: Systematic uncertainty range for Qi
        - Qc_min, Qc_max: Systematic uncertainty range for Qc
        - fano_b: Relative background path amplitude of Fano.
        """

        if b is None:
            b = 10 ** (-isolation / 20)

        b = b / (1 - b)

        if np.sin(self.phi) > b:
            logging.warning(
                "Measurement cannot be explained with assumed Fano leakage!"
            )
            self.Qi_min = np.nan
            self.Qi_max = np.nan
            self.Qc_min = np.nan
            self.Qc_max = np.nan

        # Calculate error on radius of circle
        R_mid = self.r0 * np.cos(
            self.phi
        )  # real part of the baseline normalised circle
        R_err = self.r0 * np.sqrt(np.abs(b**2 - np.sin(self.phi) ** 2))
        R_min = R_mid - R_err
        R_max = R_mid + R_err

        # Convert to ranges of quality factors
        self.Qc_min = self.Ql / (self.n_ports * R_max)
        self.Qc_max = self.Ql / (self.n_ports * R_min)
        self.Qc_mid = self.Ql / (self.n_ports * R_mid)
        self.Qi_min = self.Ql / (1 - self.n_ports * R_min)
        self.Qi_max = self.Ql / (1 - self.n_ports * R_max)
        self.Qi_mid = self.Ql / (1 - self.n_ports * R_mid)

        # Handle unphysical results
        if R_max >= 1.0 / self.n_ports:
            self.Qi_max = np.inf

        # Store results in dictionary
        self.fitresults.update(
            {
                "Qc_min": self.Qc_min,
                "Qc_max": self.Qc_max,
                "Qi_min": self.Qi_min,
                "Qi_max": self.Qi_max,
                "Qc_mid": self.Qc_mid,
                "Qi_mid": self.Qi_mid,
                "fano_b": b,
            }
        )

    def _fit_circle(self, z_data, refine_results=False):
        """
        Analytical fit of a circle to  the scattering data z_data. Cf. Sebastian
        Probst: "Efficient and robust analysis of complex scattering data under
        noise in microwave resonators" (arXiv:1410.3365v2)
        """

        # Normalize circle to deal with comparable numbers
        x_norm = 0.5 * (np.max(z_data.real) + np.min(z_data.real))
        y_norm = 0.5 * (np.max(z_data.imag) + np.min(z_data.imag))
        z_data = z_data[:] - (x_norm + 1j * y_norm)
        amp_norm = np.max(np.abs(z_data))
        z_data = z_data / amp_norm

        # Calculate matrix of moments
        xi = z_data.real
        xi_sqr = xi * xi
        yi = z_data.imag
        yi_sqr = yi * yi
        zi = xi_sqr + yi_sqr
        Nd = float(len(xi))
        xi_sum = xi.sum()
        yi_sum = yi.sum()
        zi_sum = zi.sum()
        xiyi_sum = (xi * yi).sum()
        xizi_sum = (xi * zi).sum()
        yizi_sum = (yi * zi).sum()
        M = np.array(
            [
                [(zi * zi).sum(), xizi_sum, yizi_sum, zi_sum],
                [xizi_sum, xi_sqr.sum(), xiyi_sum, xi_sum],
                [yizi_sum, xiyi_sum, yi_sqr.sum(), yi_sum],
                [zi_sum, xi_sum, yi_sum, Nd],
            ]
        )

        # Lets skip line breaking at 80 characters for a moment :D
        a0 = (
            (
                (M[2][0] * M[3][2] - M[2][2] * M[3][0]) * M[1][1]
                - M[1][2] * M[2][0] * M[3][1]
                - M[1][0] * M[2][1] * M[3][2]
                + M[1][0] * M[2][2] * M[3][1]
                + M[1][2] * M[2][1] * M[3][0]
            )
            * M[0][3]
            + (
                M[0][2] * M[2][3] * M[3][0]
                - M[0][2] * M[2][0] * M[3][3]
                + M[0][0] * M[2][2] * M[3][3]
                - M[0][0] * M[2][3] * M[3][2]
            )
            * M[1][1]
            + (
                M[0][1] * M[1][3] * M[3][0]
                - M[0][1] * M[1][0] * M[3][3]
                - M[0][0] * M[1][3] * M[3][1]
            )
            * M[2][2]
            + (-M[0][1] * M[1][2] * M[2][3] - M[0][2] * M[1][3] * M[2][1]) * M[3][0]
            + (
                (M[2][3] * M[3][1] - M[2][1] * M[3][3]) * M[1][2]
                + M[2][1] * M[3][2] * M[1][3]
            )
            * M[0][0]
            + (
                M[1][0] * M[2][3] * M[3][2]
                + M[2][0] * (M[1][2] * M[3][3] - M[1][3] * M[3][2])
            )
            * M[0][1]
            + (
                (M[2][1] * M[3][3] - M[2][3] * M[3][1]) * M[1][0]
                + M[1][3] * M[2][0] * M[3][1]
            )
            * M[0][2]
        )
        a1 = (
            (
                (M[3][0] - 2.0 * M[2][2]) * M[1][1]
                - M[1][0] * M[3][1]
                + M[2][2] * M[3][0]
                + 2.0 * M[1][2] * M[2][1]
                - M[2][0] * M[3][2]
            )
            * M[0][3]
            + (
                2.0 * M[2][0] * M[3][2]
                - M[0][0] * M[3][3]
                - 2.0 * M[2][2] * M[3][0]
                + 2.0 * M[0][2] * M[2][3]
            )
            * M[1][1]
            + (-M[0][0] * M[3][3] + 2.0 * M[0][1] * M[1][3] + 2.0 * M[1][0] * M[3][1])
            * M[2][2]
            + (-M[0][1] * M[1][3] + 2.0 * M[1][2] * M[2][1] - M[0][2] * M[2][3])
            * M[3][0]
            + (M[1][3] * M[3][1] + M[2][3] * M[3][2]) * M[0][0]
            + (M[1][0] * M[3][3] - 2.0 * M[1][2] * M[2][3]) * M[0][1]
            + (M[2][0] * M[3][3] - 2.0 * M[1][3] * M[2][1]) * M[0][2]
            - 2.0 * M[1][2] * M[2][0] * M[3][1]
            - 2.0 * M[1][0] * M[2][1] * M[3][2]
        )
        a2 = (
            (2.0 * M[1][1] - M[3][0] + 2.0 * M[2][2]) * M[0][3]
            + (2.0 * M[3][0] - 4.0 * M[2][2]) * M[1][1]
            - 2.0 * M[2][0] * M[3][2]
            + 2.0 * M[2][2] * M[3][0]
            + M[0][0] * M[3][3]
            + 4.0 * M[1][2] * M[2][1]
            - 2.0 * M[0][1] * M[1][3]
            - 2.0 * M[1][0] * M[3][1]
            - 2.0 * M[0][2] * M[2][3]
        )
        a3 = -2.0 * M[3][0] + 4.0 * M[1][1] + 4.0 * M[2][2] - 2.0 * M[0][3]
        a4 = -4.0

        def char_pol(x):
            return a0 + a1 * x + a2 * x**2 + a3 * x**3 + a4 * x**4

        def d_char_pol(x):
            return a1 + 2 * a2 * x + 3 * a3 * x**2 + 4 * a4 * x**3

        eta = spopt.newton(char_pol, 0.0, fprime=d_char_pol)

        M[3][0] = M[3][0] + 2 * eta
        M[0][3] = M[0][3] + 2 * eta
        M[1][1] = M[1][1] - eta
        M[2][2] = M[2][2] - eta

        U, s, Vt = np.linalg.svd(M)
        A_vec = Vt[np.argmin(s), :]

        xc = -A_vec[1] / (2.0 * A_vec[0])
        yc = -A_vec[2] / (2.0 * A_vec[0])
        # The term *sqrt term corrects for the constraint, because it may be
        # altered due to numerical inaccuracies during calculation
        r0 = (
            1.0
            / (2.0 * np.absolute(A_vec[0]))
            * np.sqrt(
                A_vec[1] * A_vec[1] + A_vec[2] * A_vec[2] - 4.0 * A_vec[0] * A_vec[3]
            )
        )

        return xc * amp_norm + x_norm, yc * amp_norm + y_norm, r0 * amp_norm

    def _fit_phase(self, z_data, guesses=None):
        """
        Fits the phase response of a strongly overcoupled (Qi >> Qc) resonator
        in reflection which corresponds to a circle centered around the origin
        (cf‌. phase_centered()).

        inputs:
        - z_data: Scattering data of which the phase should be fit. Data must be
                  distributed around origin ("circle-like").
        - guesses (opt.): If not given, initial guesses for the fit parameters
                          will be determined. If given, should contain useful
                          guesses for fit parameters as a tuple (fr, Ql, delay)

        outputs:
        - fr: Resonance frequency
        - Ql: Loaded quality factor
        - theta: Offset phase
        - delay: Time delay between output and input signal leading to linearly
                 frequency dependent phase shift
        """
        phase = np.unwrap(np.angle(z_data))

        # For centered circle roll-off should be close to 2pi. If not warn user.
        if np.max(phase) - np.min(phase) <= 0.7 * 2 * np.pi:  # 70% of 2pi
            logging.warning(
                f"Data does not cover a full circle (only {np.max(phase) - np.min(phase):.1f}"
                + " rad). Increase the frequency span around the resonance?"
            )
            roll_off = np.max(phase) - np.min(phase)
        else:
            roll_off = 2 * np.pi

        # Set useful starting parameters (improved 2025)
        if guesses is None:
            # Use maximum of derivative of phase as guess for fr
            phase_smooth = gaussian_filter1d(phase, 30)

            # phase_derivative = np.gradient(phase_smooth,self.f_data)
            phase_derivative = np.gradient(phase_smooth)

            theta_guess = (
                phase[np.argmax(np.abs(phase_derivative))] / 2
            )  # this is the frequency where the phase derivative is maximum
            # Guess for fr is the frequency where the phase derivative is maximum

            fr_guess = self.f_data[np.argmax(np.abs(phase_derivative))]

            # grad=np.max(np.abs(phase,self.f_data))
            Ql_guess = (
                2 * fr_guess / (self.f_data[-1] - self.f_data[0])
            )  # 2 F_max / delta_f DO NOT USE THIS
            # Estimate delay from background slope of phase (substract roll-off)
            slope = phase[-1] - phase[0] + roll_off
            delay_guess = -slope / (2 * np.pi * (self.f_data[-1] - self.f_data[0]))

            # Ql_guess = fr_guess *(grad -2*np.pi*delay_guess) / 4
        else:
            fr_guess, Ql_guess, delay_guess = guesses
        # This one seems stable and we do not need a manual guess for it
        theta_guess = 0.5 * (np.mean(phase[:5]) + np.mean(phase[-5:]))

        logging.info(
            f"Initial guesses: fr={fr_guess:.2f} Hz, Ql={Ql_guess:.2f}, theta={theta_guess:.2f}, delay={delay_guess:.2e} s "
        )
        # Fit model with less parameters first to improve stability of fit

        def residuals_Ql(params, freq=self.f_data, phase=phase):
            (Ql,) = params
            return residuals_full((fr_guess, Ql, theta_guess, delay_guess), freq, phase)

        def residuals_fr_theta(params, freq=self.f_data, phase=phase):
            fr, theta = params
            return residuals_full((fr, Ql_guess, theta, delay_guess), freq, phase)

        def residuals_delay(params, freq=self.f_data, phase=phase):
            (delay,) = params
            return residuals_full((fr_guess, Ql_guess, theta_guess, delay), freq, phase)

        def residuals_fr_Ql(params, freq=self.f_data, phase=phase):
            fr, Ql = params
            return residuals_full((fr, Ql, theta_guess, delay_guess), freq, phase)

        def residuals_full(params, freq=self.f_data, phase=phase):
            return self._phase_dist(phase - CircleFitter.phase_centered(freq, *params))

        # first only try to fit Ql
        p_final = spopt.least_squares(
            residuals_Ql, [Ql_guess], args=(self.f_data, phase), method="dogbox"
        )
        logging.info(f"Ql fit results: {p_final.x}")
        (Ql_guess,) = p_final.x

        p_final = spopt.least_squares(
            residuals_fr_theta,
            [fr_guess, theta_guess],
            args=(self.f_data, phase),
            method="dogbox",
        )
        logging.info(f"fr, theta fit results: {p_final.x}")
        fr_guess, theta_guess = p_final.x

        p_final = spopt.least_squares(
            residuals_delay, [delay_guess], args=(self.f_data, phase), method="dogbox"
        )
        logging.info(f"delay fit results: {p_final.x}")
        (delay_guess,) = p_final.x

        p_final = spopt.least_squares(
            residuals_fr_Ql,
            [fr_guess, Ql_guess],
            args=(self.f_data, phase),
            method="dogbox",
        )
        logging.info(f"fr, Ql fit results: {p_final.x}")
        fr_guess, Ql_guess = p_final.x

        p_final = spopt.least_squares(
            residuals_full,
            [fr_guess, Ql_guess, theta_guess, delay_guess],
            args=(self.f_data, phase),
            method="dogbox",
        )

        logging.info(f"phase fit results: {p_final.x}")
        return p_final.x

    @classmethod
    def phase_centered(cls, f, fr, Ql, theta, delay=0.0):
        """
        Yields the phase response of a strongly overcoupled (Qi >> Qc) resonator
        in reflection which corresponds to a circle centered around the origin.
        Additionally, a linear background slope is accounted for if needed.

        inputs:
        - fr: Resonance frequency
        - Ql: Loaded quality factor (and since Qi >> Qc also Ql = Qc)
        - theta: Offset phase
        - delay (opt.): Time delay between output and input signal leading to
                        linearly frequency dependent phase shift
        """
        return (
            theta
            - 2 * np.pi * delay * (f - fr)
            + 2.0 * np.arctan(2.0 * Ql * (1.0 - f / fr))
        )

    def _phase_dist(self, angle):
        """
        Maps angle [-2pi, +2pi] to phase distance on circle [0, pi]
        """
        return np.pi - np.abs(np.pi - np.abs(angle))

    def _periodic_boundary(self, angle):
        """
        Maps arbitrary angle to interval [-np.pi, np.pi)
        """
        return (angle + np.pi) % (2 * np.pi) - np.pi

    def _get_residuals(self):
        """
        Calculates deviation of measured data from fit.
        """
        return self.z_data_norm - self.Sij(
            self.f_data, self.fr, self.Ql, self.Qc, self.phi
        )

    def _get_covariance(self):
        """
        Calculates reduced chi square and covariance matrix for fit.
        """
        residuals = self._get_residuals()
        chi = np.abs(residuals)
        # Unit vectors pointing in the correct directions for the derivative
        directions = residuals / chi
        # Prepare for fast construction of Jacobian
        conj_directions = np.conj(directions)

        # Construct transpose of Jacobian matrix
        Jt = np.array(
            [
                np.real(self._dSij_dfr() * conj_directions),
                np.real(self._dSij_dQl() * conj_directions),
                np.real(self._dSij_dabsQc() * conj_directions),
                np.real(self._dSij_dphi() * conj_directions),
            ]
        )
        A = np.dot(Jt, np.transpose(Jt))
        # 4 fit parameters reduce degrees of freedom for reduced chi square
        chi_square = 1.0 / float(len(self.f_data) - 4) * np.sum(chi**2)
        try:
            cov = np.linalg.inv(A) * chi_square
        except:
            cov = None
        return chi_square, cov

    def _dSij_dfr(self):
        """
        Derivative of Sij w.r.t. fr
        """
        return (
            -4j
            * self.Ql**2
            * np.exp(1j * self.phi)
            * self.f_data
            / (
                self.n_ports
                * self.absQc
                * (self.fr + 2j * self.Ql * (self.f_data - self.fr)) ** 2
            )
        )

    def _dSij_dQl(self):
        """
        Derivative of Sij w.r.t. Ql
        """
        return (
            -2.0
            * np.exp(1j * self.phi)
            / (
                self.n_ports
                * self.absQc
                * (1.0 + 2j * self.Ql * (self.f_data / self.fr - 1)) ** 2
            )
        )

    def _dSij_dabsQc(self):
        """
        Derivative of Sij w.r.t. absQc
        """
        return (
            2.0
            * self.Ql
            * np.exp(1j * self.phi)
            / (
                self.n_ports
                * self.absQc**2
                * (1.0 + 2j * self.Ql * (self.f_data / self.fr - 1))
            )
        )

    def _dSij_dphi(self):
        """
        Derivative of Sij w.r.t. phi
        """
        return (
            -2j
            * self.Ql
            * np.exp(1j * self.phi)
            / (
                self.n_ports
                * self.absQc
                * (1.0 + 2j * self.Ql * (self.f_data / self.fr - 1))
            )
        )

    """
    Functions for plotting results
    """

    def plotall(self):
        if not plot_enable:
            raise ImportError("matplotlib not found")
        real = self.z_data_raw.real
        imag = self.z_data_raw.imag
        real2 = self.z_data_sim.real
        imag2 = self.z_data_sim.imag
        real_norm = self.z_data_norm.real
        imag_norm = self.z_data_norm.imag
        # delay corrected only
        delay_corr_real = self.z_data_corr.real
        delay_corr_imag = self.z_data_corr.imag
        c = self.fitresults["c"]
        offrespoint = self.offrespoint
        # Find the index of the frequency closest to the resonance frequency
        res_idx = np.argmin(np.abs(self.f_data - self.fr))
        respoint = self.z_data_corr[res_idx]

        fig, axs = plt.subplots(
            3,
            2,
            gridspec_kw={"width_ratios": [1, 1], "height_ratios": [1, 1, 1]},
            figsize=(8, 11),
        )
        # axs[0,0].axvline(0, c="k", ls="--", lw=1)
        axs[0, 0].axhline(0, c="k", ls="--", lw=1, alpha=0.6)
        axs[0, 0].plot(
            real[::5],
            imag[::5],
            label="rawdata",
            marker="o",
            markersize=5,
            markerfacecolor="None",
            ls="",
        )
        axs[0, 0].plot(real2, imag2, label="fit", lw=2)
        axs[0, 0].set_title("Raw data and fit", fontsize=14)

        axs[0, 0].set_aspect("equal", adjustable="datalim")
        axs[0, 0].set_xlabel("Re(S21)", fontsize=12)
        axs[0, 0].set_ylabel("Im(S21)", fontsize=12)
        axs[0, 0].legend()

        imag - self.offrespoint.imag
        axs[0, 1].set_aspect("equal", adjustable="datalim")
        axs[0, 1].axvline(1, c="k", ls="--", lw=1, alpha=0.6)
        axs[0, 1].axhline(0, c="k", ls="--", lw=1, alpha=0.6)
        # axs[0,1].scatter(real2,imag2,label='sim-data',s=3,color='b')
        axs[0, 1].scatter(
            real_norm,
            imag_norm,
            label="norm-data",
            s=15,
            facecolors="None",
            edgecolors="r",
        )
        # sim_norm is simulated without a,alpha,delay; has phi but still a circle nevertheless
        axs[0, 1].plot(
            self.z_data_sim_norm.real,
            self.z_data_sim_norm.imag,
            color="k",
            ls="-",
            label="sim-data (no a,alp,del)",
        )
        # axs[0,1].plot(self.z_data_sim_norm.real,self.z_data_sim_norm.imag,'y-',linewidth=100*self.a*self.sigma,alpha=0.5)
        axs[0, 1].set_title("Normalized data w/o (a, $ \\alpha,\\tau $ )", fontsize=14)
        axs[0, 1].set_xlabel("Re(S21)", fontsize=12)
        axs[0, 1].set_ylabel("Im(S21)", fontsize=12)
        axs[0, 1].legend(loc="best", fontsize=8)

        # imag_cannonical=imag-self.offrespoint.imag

        axs[1, 0].plot(
            self.f_data * 1e-9,
            np.absolute(self.z_data_raw),
            label="rawdata",
            marker="o",
            markersize=5,
            markerfacecolor="None",
            ls="",
        )
        axs[1, 0].plot(
            self.f_data * 1e-9, np.absolute(self.z_data_sim), label="fit", lw=1.5
        )
        axs[1, 0].set_xlabel("f (GHz)", fontsize=12)
        axs[1, 0].set_ylabel("$ | S21 | $", fontsize=12)
        axs[1, 0].legend()

        axs[1, 1].plot(
            self.f_data * 1e-9,
            np.angle(self.z_data_raw),
            label="rawdata",
            marker="o",
            markersize=5,
            markerfacecolor="None",
            ls="",
        )
        axs[1, 1].plot(self.f_data * 1e-9, np.angle(self.z_data_sim), label="fit")
        axs[1, 1].set_xlabel("f (GHz)", fontsize=12)
        axs[1, 1].set_ylabel("arg(|S21|)", fontsize=12)
        axs[1, 1].legend()

        a = np.exp(1j * self.fitresults["alpha"])  # alpha
        phi_phase = np.exp(-1j * self.fitresults["phi"])
        self.fitresults["r0"]

        diam = np.linalg.norm(respoint - self.offrespoint)  # diameter of the circle
        axs[2, 0].axvline(0, c="k", ls="--", lw=0.5)
        axs[2, 0].axhline(0, c="k", ls="--", lw=0.5)
        axs[2, 0].scatter(
            delay_corr_real,
            delay_corr_imag,
            label="Delay removed",
            s=15,
            facecolors="None",
            edgecolors="orange",
        )
        axs[2, 0].scatter(
            np.real(c), np.imag(c), color="r", s=50, edgecolors="y", linewidths=1
        )

        axs[2, 0].scatter(
            np.real(self.offrespoint),
            np.imag(self.offrespoint),
            marker="X",
            color="k",
            s=100,
            edgecolors="y",
            linewidths=2,
        )  #
        axs[2, 0].scatter(
            np.real(respoint),
            np.imag(respoint),
            marker="x",
            color="g",
            s=100,
            edgecolors="None",
            linewidths=1,
            label="resonance point",
        )
        axs[2, 0].plot(
            np.real([respoint, offrespoint]),
            np.imag([respoint, offrespoint]),
            "b:",
            alpha=0.3,
        )  #

        axs[2, 0].annotate(
            f"d(2r)={diam:.2f}",
            xy=(0.45, 0.6),
            xycoords="axes fraction",
            fontsize=10,
            color="b",
        )
        axs[2, 0].set_title(
            f'Delay removed ( delay-rem={self.fitresults["delay_remaining"]:.2e})',
            fontsize=14,
        )
        axs[2, 0].set_aspect("equal", adjustable="datalim")
        axs[2, 0].legend(loc=3, fontsize=8)

        # remove delay, then normalise by alpha , a
        # here a=alpha
        self.z_data_corr / a / self.a
        norm = (
            self.z_data_corr - offrespoint
        ) / a  # subtract the off res point -> puts the off res-point to 0,0
        # then roate by a (alpha)

        # norm=self.z_data_corr

        # norm_scale=norm * imp
        ## rotate by phi, and shift it to 1,0
        norm_rot = norm.copy() * phi_phase + 1

        # relate it to a normalised circle. corrected / a/ alpha/ phi
        normalised = self.z_data_corr / self.a / a
        s21_term = (1 - normalised) * phi_phase  # impedance mismatch corrected
        mismatch_corrected = 1 - s21_term

        # here we normalise the delay-corrected S21 / alpha / a and then
        # (1- normalised ) * phi_rotate for impedance mismatch
        # 1- mismatched = S21 corrected

        # axs[2,1].scatter((c/a/self.a).real,(c/a/self.a).imag,label='c/a/alpha',s=50,edgecolors='y',linewidths=1,color='r',marker='x')

        # How would it look if we maually corrected the phi after delay removal
        # let's center the delay-off-res point because the point of rotation is the off res point
        centered_delay_corr = self.z_data_corr - offrespoint
        # then rorate by alpha and shift to 1,0
        centered_delay_corr_rot = (
            centered_delay_corr * phi_phase / a + 1
        )  # rotate by phi
        sim_norm_fit = self.Sij(
            self.f_data,
            self.fr,
            self.Ql,
            self.absQc,
        )  # everything else zero
        # sim_norm_fit=self.a*(sim_norm_fit-1)+1
        sim_unnorm_fit = self.a * (sim_norm_fit - 1) + 1

        axs[2, 1].set_aspect("equal", adjustable="datalim")
        axs[2, 1].axvline(1, c="k", ls="--", lw=0.5)
        axs[2, 1].axvline(0, c="k", ls="--", lw=0.5)

        axs[2, 1].axhline(0, c="k", ls="--", lw=0.5)

        # axs[2,1].scatter(final.real,final.imag,label='data-normed',s=3,color='b')
        # axs[2,1].scatter(c.real,c.imag,marker='X',s=100,color='g')

        # axs[2,1].scatter(centered_delay_corr.real,centered_delay_corr.imag,label='delay-corrected',s=3,color='green')
        # axs[2,1].scatter(centered_delay_corr_rot.real,centered_delay_corr_rot.imag,label='delay-corrected+phi',s=3,color='orange')

        axs[2, 1].scatter(
            norm_rot.real,
            norm_rot.imag,
            label="corrected/alpha/phi",
            s=15,
            color="k",
            facecolors="None",
        )
        axs[2, 1].scatter(
            mismatch_corrected.real,
            mismatch_corrected.imag,
            label="corrected/alpha/phi/a",
            s=15,
            color="orange",
            marker="o",
        )

        axs[2, 1].plot(
            sim_norm_fit.real,
            sim_norm_fit.imag,
            label="Sim-norm-absQc",
            ls="-",
            lw=1,
            color="b",
        )
        axs[2, 1].plot(
            sim_unnorm_fit.real,
            sim_unnorm_fit.imag,
            label="a*(Sim-unnorm-absQc)",
            ls="-",
            lw=1,
            color="r",
        )

        axs[2, 1].set_title("(1- data/a/alpha) phi-corrected")
        # axs[2,1].plot(self.z_data_sim_norm.real,self.z_data_sim_norm.imag,'m-',label='sim-n x r - rot')

        # axs[2,1].scatter(norm_rot.real,norm_rot.imag,label='data-n x r - rot',s=3,color='k')

        # axs[2,1].scatter(norm.real/self.r0/2,norm.imag/self.r0/2,label='corr-data-normed',s=3,color='g')

        axs[2, 1].set_xlabel("Re(S21)", fontsize=12)
        axs[2, 1].set_ylabel("Im(S21)", fontsize=12)
        axs[2, 1].legend(loc=1, fontsize=8)

        fig.tight_layout()
        plt.show()

    def plotcalibrateddata(self):
        if not plot_enable:
            raise ImportError("matplotlib not found")
        real = self.z_data_norm.real
        imag = self.z_data_norm.imag
        plt.subplot(221)
        plt.plot(real, imag, label="rawdata")
        plt.xlabel("Re(S21)")
        plt.ylabel("Im(S21)")
        plt.legend()
        plt.subplot(222)
        plt.plot(self.f_data * 1e-9, np.absolute(self.z_data_norm), label="rawdata")
        plt.xlabel("f (GHz)")
        plt.ylabel("|S21|")
        plt.legend()
        plt.subplot(223)
        plt.plot(self.f_data * 1e-9, np.angle(self.z_data_norm), label="rawdata")
        plt.xlabel("f (GHz)")
        plt.ylabel("arg(|S21|)")
        plt.legend()
        plt.show()

    def plotrawdata(self):
        if not plot_enable:
            raise ImportError("matplotlib not found")
        if self.z_data_raw is None:
            raise ValueError("z_data_raw is None. Cannot plot raw data.")
        real = self.z_data_raw.real
        imag = self.z_data_raw.imag
        plt.subplot(221)
        plt.plot(real, imag, label="rawdata")
        plt.xlabel("Re(S21)")
        plt.ylabel("Im(S21)")
        plt.legend()
        plt.subplot(222)
        plt.plot(self.f_data * 1e-9, np.absolute(self.z_data_raw), label="rawdata")
        plt.xlabel("f (GHz)")
        plt.ylabel("|S21|")
        plt.legend()
        plt.subplot(223)
        plt.plot(self.f_data * 1e-9, np.angle(self.z_data_raw), label="rawdata")
        plt.xlabel("f (GHz)")
        plt.ylabel("arg(|S21|)")
        plt.legend()
        plt.show()

    def get_single_photon_limit(self, unit="dBm", diacorr=True):
        """
        returns the amout of power in units of W necessary
            to maintain one photon on average in the cavity
            unit can be 'dBm' or 'watt'
        """
        if self.fitresults != {}:
            fr = self.fitresults["fr"]
            if diacorr:
                k_c = 2 * np.pi * fr / self.fitresults["Qc"]
                k_i = 2 * np.pi * fr / self.fitresults["Qi"]
            else:
                k_c = 2 * np.pi * fr / self.fitresults["Qc_abs"]
                k_i = 2 * np.pi * fr / self.fitresults["Qi_no_dia_corr"]
            if unit == "dBm":
                return Watt2dBm(
                    1.0
                    / (4.0 * k_c / (2.0 * np.pi * const.hbar * fr * (k_c + k_i) ** 2))
                )
            elif unit == "watt":
                return 1.0 / (
                    4.0 * k_c / (2.0 * np.pi * const.hbar * fr * (k_c + k_i) ** 2)
                )
        else:
            logging.warning("Please perform the fit first", UserWarning)
            return None

    def get_photons_in_resonator(self, power=0, unit="dBm", diacorr=True):
        """
        returns the average number of photons
        for a given power in units of W
        unit can be 'dBm' or 'watt'
        """
        logging.info("power: %s", power)
        if self.fitresults != {}:
            if unit == "dBm":
                power = dBm2Watt(power)
            fr = self.fitresults["fr"]
            if diacorr:
                k_c = 2 * np.pi * fr / self.fitresults["Qc"]
                k_i = 2 * np.pi * fr / self.fitresults["Qi"]
            else:
                k_c = 2 * np.pi * fr / self.fitresults["Qc_abs"]
                k_i = 2 * np.pi * fr / self.fitresults["Qi_no_dia_corr"]
            return (
                4.0 * k_c / (2.0 * np.pi * const.hbar * fr * (k_c + k_i) ** 2) * power
            )
        else:
            logging.warning("Please perform the fit first", UserWarning)
            return None


# class reflection_port(circuit):
#     """
#     Circlefit class for single-port resonator probed in reflection.
#     """

#     # See Sij of circuit class for explanation
#     n_ports = 1.


class notch_port(CircleFitter):
    """
    Circlefit class for two-port resonator probed in transmission.
    """

    # See Sij of circuit class for explanation
    n_ports = 2
