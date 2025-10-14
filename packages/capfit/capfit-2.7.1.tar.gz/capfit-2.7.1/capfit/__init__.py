__version__ = "2.7.1"

from .capfit import capfit, lsq_box, lsq_lin, lsq_lin_cvxopt, cov_err, lsq_eq
from .format_values_with_errors import format_values_with_errors

__all__ = [
    "capfit",
    "lsq_box", 
    "lsq_lin", 
    "lsq_lin_cvxopt", 
    "cov_err", 
    "lsq_eq",
    "format_values_with_errors"
]

