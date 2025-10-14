"""
Copyright (C) 2015-2025, Michele Cappellari
E-mail: michele.cappellari_at_physics.ox.ac.uk

This software is provided as is without any warranty whatsoever.
Permission to use, for non-commercial purposes is granted.
Permission to modify for personal or internal use is granted,
provided this copyright and disclaimer are included unchanged
at the beginning of the file. All other rights are reserved.
In particular, redistribution of the code is not allowed.

###############################################################################

Version History
---------------
- V2.1.0: MC, Oxford, 21 July 2025
    Combined text/latex loops. 
    Renamed class to format_values_with_errors .
    Included in CapFit package.
- V2.0.2: MC, Oxford, 15 October 2022
    Simplified code with .split().
- V2.0.1: MC, Oxford, 10 January 2018
    Removes LaTeX syntax from plain string.
- V2.0.0: MC, Oxford, 21 December 2017
    Properly deal with values in exponent form and zero values/errors.
    Correctly show all significant trailing zeros.
- V1.0.2: MC, Oxford, 22 November 2017
    Use Python 3.6 f-strings.
- V1.0.1: MC, Oxford, 22 July 2015
    Prevent negative precisions.
- V1.0.0: Michele Cappellari, Oxford, 17 June 2015
    Extracted from my own lts_linefit
"""

#------------------------------------------------------------------------------

import re
import numpy as np

class format_values_with_errors:
    """Formats and prints values with their uncertainties.

    This class takes numerical values, their associated errors, and labels,
    and formats them into human-readable strings. The uncertainties are rounded
    to two significant digits, and the values are rounded to the same level of
    precision. It intelligently handles scientific notation and cases with zero
    values or errors.

    It produces both a plain text version for console output and a LaTeX
    version for inclusion in documents.

    Parameters
    ----------
    par : array_like
        The parameter values.
    sig : array_like
        The corresponding 1-sigma uncertainties. Must have the same size as `par`.
    labels : array_like of str
        The names for each parameter. Can include LaTeX syntax (e.g., "$\\sigma$").
        Must have the same size as `par`.

    Attributes
    ----------
    .plain : str
        Multi-line string with parameters and errors formatted for plain text.
    .latex : str
        Multi-line string with parameters and errors formatted for LaTeX.
    """
    def __init__(self, par, sig, labels):

        par, sig, labels = map(np.atleast_1d, [par, sig, labels])
        assert par.size == sig.size == labels.size, "Input vectors must have the same size"
        assert np.all(sig >= 0), "Errors cannot be negative"

        digits = np.full_like(par, 2)
        prec = np.full_like(par, 2)

        w = sig > 0
        sig[w] = [float(f"{x:0.2g}") for x in sig[w]]       # Round to two significant digits
        prec[w] = 1 - np.floor(np.log10(np.abs(sig[w])))    # precision of second digit
        par[w] = np.round(par[w]*10**prec[w])/10**prec[w]   # Round to precision of errors

        w &= par != 0
        digits[w] = np.ceil(np.log10(np.abs(par[w]))) + prec[w]
        digits = digits.clip(0).astype(int)
        prec = prec.astype(int)

        # Removes LaTeX syntax for plain text printing
        labels_plain = [re.sub(r'\$|{|}|\\(?:mathrm|rm) ?|\\', '', s) for s in labels]
        chars = str(max(map(len, labels_plain)))

        # Generate plain text and LaTeX strings in a single loop
        plain_lines = []
        latex_lines = []
        for t, t_plain, d, pr, p, s in zip(labels, labels_plain, digits, prec, par, sig):
            val, err = f"{p:0.{d}g}", f"{s:0.2g}"
            if s == 0:
                if "e" in val:
                    e = int(val.split('e')[1])
                    p_scaled = p / 10**e
                    plain_lines.append(f"{t_plain:>{chars}} = {p_scaled:0.4g}e{e}")
                    latex_lines.append(f"{t} = {p_scaled:0.4g}$\\times10^{{{e}}}$")
                else:
                    plain_lines.append(f"{t_plain:>{chars}} = {p:0.4g}")
                    latex_lines.append(f"{t} = {p:0.4g}")
            elif "e" in val or ("e" in err and p == 0):
                e = int(val.split('e')[1] if "e" in val else err.split('e')[1])
                p_scaled, s_scaled = p / 10**e, s / 10**e
                fmt = f"0.{pr+e}f"
                plain_lines.append(f"{t_plain:>{chars}} = ({p_scaled:{fmt}} +/- {s_scaled:{fmt}})e{e}")
                latex_lines.append(f"{t} = ({p_scaled:{fmt}} $\\pm$ {s_scaled:{fmt}})$\\times10^{{{e}}}$")
            else:
                fmt = f"0.{pr}f"
                plain_lines.append(f"{t_plain:>{chars}} = {p:{fmt}} +/- {s:{fmt}}")
                latex_lines.append(f"{t} = {p:{fmt}} $\\pm$ {s:{fmt}}")

        self.plain = "\n".join(plain_lines)
        self.latex = "\n".join(latex_lines)

#------------------------------------------------------------------------------

if __name__ == '__main__':

    """Example usage of the format_values_with_errors  function."""

    s = np.pi
    txt = format_values_with_errors (
        [s*1e2,  s*1e9,       3.00423e-29,   0.0,  s*1e-3, s*1e5, 10.234, 0.0408, 0.341,  4.985e6],
        [0.1999, 0.711e9,       0.567e-29, 1.23e-10, 0.23,   0.0,    0.0,   0.12, 0.0999, 0.988e6],
        ["a", "$\\sigma_{\\rm JAM}$", "c",   "d",     "e",   "f",    "g",    "h",  "i", "$M_\\mathrm{BH}$"]
    )
    print("\n" + txt.plain)
    print("\n" + txt.latex)
    
    txt = format_values_with_errors ([8165.666], [338.9741], ["a"])
    print("\n" + txt.plain)
    print("\n" + txt.latex) 
    