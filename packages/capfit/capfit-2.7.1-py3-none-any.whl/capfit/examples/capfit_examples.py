################################################################################
#
# Copyright (C) 2017-2025, Michele Cappellari
# E-mail: michele.cappellari_at_physics.ox.ac.uk
#
# Updated versions of the software are available from the web page
# https://pypi.org/project/capfit/
#
# This software is provided as is without any warranty whatsoever.
# Permission to use, for non-commercial purposes is granted.
# Permission to modify for personal or internal use is granted,
# provided this copyright and disclaimer are included unchanged
# at the beginning of the file. All other rights are reserved.
#
################################################################################
#
# V1.0.0: By Michele Cappellari, Oxford, 15 June 2017
# V1.0.1: Updated for latest capfit version. MC, Oxford, 19 July 2024
# V1.1.0: Updated to use format_values_with_errors. MC, Oxford, 20 July 2025
#
################################################################################

import numpy as np
import matplotlib.pyplot as plt

import capfit

################################################################################

def model(p, x, a):

    return p[0]*np.exp(-0.5*(x - p[1]/a)**2/p[2]**2)

################################################################################

def example_func(p, x=None, y=None, yerr=None, a=1.0):

    ymod = model(p, x, a)
    resid = (y - ymod)/yerr

    return resid

################################################################################

a = 1.0
prng = np.random.default_rng(123)  # Give seed for reproducible results
x = np.linspace(-3, 3, 100)
p_true = np.array([2., -1., 0.5])
y = model(p_true, x, a)
yerr = np.full_like(y, 0.1)
y += prng.normal(0, yerr, x.size)
p_0 = np.array([1., 1., 1.])
kwargs = {'x': x, 'y': y, 'yerr': yerr, 'a': a}

print("\n#### Example unconstrained case ####\n")
res = capfit.capfit(example_func, p_0, kwargs=kwargs, verbose=2, diff_step=0.01)

print("\n#### Example tied parameters ####\n")
res = capfit.capfit(example_func, p_0, kwargs=kwargs, tied=['', '-p[0]/2', ''], verbose=2, abs_step=0.01)

print("\n#### Example fixed parameters ####\n")
res = capfit.capfit(example_func, [1, 1, 0.5], kwargs=kwargs, fixed=[0, 0, 1], verbose=2)

print("\n#### Example bounds on parameters ####\n")
res = capfit.capfit(example_func, p_0, kwargs=kwargs, verbose=2,
                bounds=[(-np.inf, -0.95, 0.55), np.inf])

# I multiply one of the parameters by a large number:
# without Jacobian scaling the procedure would fail miserably
a = 1e10
p_0 = [1, a, 1]
kwargs = {'x': x, 'y': y, 'yerr': yerr, 'a': a}
print("\n#### Example Jacobian scaling with unscaled variables ####\n")
res = capfit.capfit(example_func, p_0, kwargs=kwargs, x_scale='jac', verbose=2)

fig, ax = plt.subplots()
ax.plot(x, y, 'o', label="Data")
ax.plot(x, model(res.x, x, a), label="Best Fit")
plt.xlabel("x")
plt.ylabel("y")

# Add text with best-fit parameters
labels = ["$y_{\\rm max}$", "$x_0*a$", "$\\sigma_x$"]
txt = capfit.format_values_with_errors(res.x, res.x_err, labels)
ax.text(0.98, 0.98, txt.latex, transform=ax.transAxes, va='top', ha='right')
print("Best-fitting Parameters:\n", txt.plain)

ax.legend()
plt.show()
