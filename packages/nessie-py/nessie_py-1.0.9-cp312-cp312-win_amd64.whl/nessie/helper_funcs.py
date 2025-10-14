"""
Module for quality of life helper functions which are not core to the algorithm.
"""

import warnings
from enum import Enum
from typing import Union

import numpy as np
from scipy.integrate import quad
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from statsmodels.nonparametric.kde import KDEUnivariate

from nessie_py import calculate_s_score, gen_randoms
from .cosmology import FlatCosmology


def gen_random_redshifts(
    redshifts: np.ndarray[float],
    mags: np.ndarray[float],
    z_lim: float,
    maglim: float,
    cosmo: FlatCosmology,
    n_clone: int = 400,
    iterations: int = 10,
) -> np.ndarray[float]:
    """
    Automatically models the n(z) using a randoms catalogue. This can be used to gen the density
    function.
    """

    return gen_randoms(
        redshifts,
        mags,
        z_lim,
        maglim,
        n_clone,
        iterations,
        cosmo.omega_m,
        cosmo.omega_k,
        cosmo.omega_lambda,
        cosmo.hubble_constant,
    )


def create_density_function(
    redshifts: np.ndarray,
    total_counts: int,
    survey_fractional_area: float,
    cosmology: FlatCosmology,
    binwidth: int = 40,
    interpolation_n: int = 10_000,
):
    """
    Running density function estimation (rho(z))

    Parameters
    ----------
    redshifts : array_like
        Redshift values used to estimate the redshift distribution.
    total_counts : float
        Total number of objects in the redshift survey.
    survey_fractional_area : float
        Fraction of the sky covered by the survey (relative to 4π steradians).
    cosmology : CustomCosmology
        A cosmology object with methods:
            - comoving_distance(z)
            - z_at_comoving_dist(d)
    binwidth : float
        Bin width in comoving Mpc (default = 40).
    interpolation_n : int
        Number of bins used for interpolation (default = 10,000).

    Returns
    -------
    rho_z_func : callable
        A function rho(z) that gives the running density at a given redshift.
    """
    comoving_distances = cosmology.comoving_distance(redshifts)

    kde = KDEUnivariate(comoving_distances)
    kde.fit(bw=binwidth, fft=True, gridsize=interpolation_n, cut=0)
    kde_x = kde.support
    kde_y = kde.density

    kde_func = interp1d(kde_x, kde_y, bounds_error=False, fill_value="extrapolate")

    # Running integral over each bin
    running_integral = np.array(
        [quad(kde_func, max(x - binwidth / 2, 0), x + binwidth / 2)[0] for x in kde_x]
    )

    # Running comoving volume per bin
    upper_volumes = (4 / 3) * np.pi * (kde_x + binwidth / 2) ** 3
    lower_volumes = (4 / 3) * np.pi * (kde_x - binwidth / 2) ** 3
    running_volume = survey_fractional_area * (upper_volumes - lower_volumes)

    # Convert comoving distance to redshift
    z_vals = cosmology.z_at_comoving_distances(kde_x)
    rho_vals = (total_counts * running_integral) / running_volume

    # Interpolate rho(z)
    rho_z_func = interp1d(
        z_vals, rho_vals, bounds_error=False, fill_value="extrapolate"
    )

    return rho_z_func


def create_density_function_be93(
    redshifts: np.ndarray, 
    survey_fractional_area: float, 
    cosmology: FlatCosmology, 
    z_binwidth: float = 0.002, 
):
    """
    Running density function estimation (rho(z)) using a generalized form of the Baugh & Efstathiou 1993 methodology

    Parameters
    ----------
    redshifts : array_like
        Redshift values used to estimate the redshift distribution.
    survey_fractional_area : float
        Fraction of the sky covered by the survey (relative to 4π steradians).
    cosmology : CustomCosmology
        A cosmology object with methods:
            - differential_covol(z)
    z_binwidth : float
        Redshift bin width (default = 0.002).

    Returns
    -------
    rho_z_func : callable
        A function rho(z) that gives the running density at a given redshift.
    """
    nz = round((max(redshifts) - min(redshifts)) / z_binwidth)
    zrange = (min(redshifts), max(redshifts))
    counts, bin_edges = np.histogram(redshifts, bins=nz, range=zrange)
    z_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    dz = bin_edges[1] - bin_edges[0]
    counts_per_dz = counts.astype(float) / dz

    def _dN(z, A_m, z_c, alpha, beta):
        return A_m * z**alpha * np.exp(-(z / z_c)**(beta))

    popt, _ = curve_fit(_dN, z_centers, counts_per_dz, p0=(counts_per_dz.max(), np.median(redshifts), 2, 1.5), bounds=(0, np.inf))
    z_grid = np.linspace(zrange[0], zrange[1], nz+1)
    dn_dz = _dN(z_grid, *popt)

    dv_dz = cosmology.differential_covol(z_grid) * (survey_fractional_area * (4*np.pi))

    rho_z = dn_dz / dv_dz
    rho_z_func = interp1d(z_grid, rho_z, bounds_error=False, fill_value="extrapolate")

    return rho_z_func


def calculate_s_total(
    measured_ids: np.ndarray[int],
    mock_group_ids: np.ndarray[int],
    min_group_size: int = 2,
) -> float:
    """
    Comparing measured groups to mock catalogue groups
    """
    return calculate_s_score(
        np.astype(measured_ids, int),
        np.astype(mock_group_ids, int),
        int(min_group_size),
    )


class ValidationType(Enum):
    """
    All the types of things we can validate
    """

    RA = "ra"
    DEC = "dec"
    REDSHIFT = "redshift"
    ABS_MAG = "absolute_mag"
    COMPLETENESS = "completeness"
    B0 = "b0"
    R0 = "r0"
    VEL_ERR = "vel_err"
    ANGLE = "angle"


def validate(value: np.ndarray[float] | float, valid_type: ValidationType) -> None:
    """
    Validates the given input which can be either an array or a float
    """

    # Checking arrays don't have non-numeric values
    if valid_type in {
        ValidationType.RA,
        ValidationType.DEC,
        ValidationType.ABS_MAG,
        ValidationType.REDSHIFT,
        ValidationType.COMPLETENESS,
        ValidationType.VEL_ERR,
        ValidationType.ANGLE,
    }:
        value = np.asarray(value)
        if not np.issubdtype(value.dtype, np.number):
            raise TypeError(f"{valid_type.value} must be numeric.")
        if np.isnan(value).any():
            raise ValueError(f"{valid_type.value} contains NaNs.")
        if np.isinf(value).any():
            raise ValueError(f"{valid_type.value} contains infinite values.")

    # Match-case for type-specific logic
    match valid_type:
        case ValidationType.RA:
            if np.any((value < 0) | (value > 360)):
                raise ValueError("RA values must be between 0 and 360.")

        case ValidationType.DEC:
            if np.any((value < -90) | (value > 90)):
                raise ValueError("Dec values must be between -90 and 90.")

        case ValidationType.REDSHIFT:
            if np.any(value < 0):
                raise ValueError("Redshifts cannot be negative.")
            if np.any(value > 1100):
                warnings.warn("Warning: redshifts are very large!")

        case ValidationType.ABS_MAG:
            if np.any((value > -4) | (value < -50)):
                warnings.warn("Warning: absolute magnitudes look unusual.")

        case ValidationType.COMPLETENESS:
            if np.any((value < 0) | (value > 1)):
                raise ValueError("Completeness must be between 0 and 1.")

        case ValidationType.VEL_ERR:
            if np.any(value < 0):
                raise ValueError("Velocity errors must be greater than 0.")
            if np.any(value > 2000):
                warnings.warn(
                    "Warning: velocity errors seem very large. Are units correct?"
                )

        case ValidationType.B0 | ValidationType.R0:
            if not isinstance(value, (float, int)):
                raise TypeError(f"{valid_type.value} must be a scalar number.")
            if value < 0:
                raise ValueError(f"{valid_type.value} cannot be negative.")

        case ValidationType.ANGLE:
            if np.any((value < 0) | (value > 360)):
                raise ValueError("Angle must be in degrees between 0 and 360.")

        case _:
            raise ValueError(
                f"Unknown property type: {valid_type.value}. Likely Enum needs updating."
            )


def remap_ids(id_array: np.ndarray[Union[int, str, float]]) -> np.ndarray[int]:
    """
    Renames the ids which could be in string, float, or long int into a safe int32 format.
    """
    unique_vals = np.unique(id_array)
    unique_vals = unique_vals[unique_vals != -1]
    unique_vals = unique_vals[unique_vals != "-1"]  # for string cases
    mapping = {val: i + 1 for i, val in enumerate(unique_vals)}  # plus to remove 0
    mapping[-1] = -1
    return np.vectorize(mapping.get)(id_array)
