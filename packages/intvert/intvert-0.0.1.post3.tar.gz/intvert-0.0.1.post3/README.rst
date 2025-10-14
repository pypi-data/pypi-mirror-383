=======
intvert
=======

intvert is a pure Python package for inversion of 1D and 2D integer arrays from partial DFT samples. This package contains the codebase for the paper [LV]_. See the full documentation `here <https://intvert.readthedocs.io/en/latest/index.html>`_.

Examples
--------

An example usage of the sampling and inversion procedures in 2D for a large binary matrix.

>>> import intvert
>>> import numpy as np
>>> import gmpy2 
>>> 
>>> gen = np.random.default_rng(0)
>>> signal = gen.integers(0, 2, (30, 40)) # generate random binary matrix signal
>>> signal
array([[1, 1, 1, ..., 0, 0, 0],
       [0, 0, 0, ..., 1, 1, 0],
       [1, 1, 0, ..., 0, 1, 0],
       ...,
       [0, 1, 0, ..., 1, 1, 1],
       [1, 1, 1, ..., 0, 0, 1],
       [1, 1, 1, ..., 1, 1, 0]], shape=(30, 40)) 
>>> with gmpy2.get_context() as c: # perform sampling and inversion with increased precision
...     c.precision = 100
...     sampled = intvert.sample_2D(signal)
...     inverted = intvert.invert_2D(signal, beta2=1e20)
... 
>>> inverted
array([[1, 1, 1, ..., 0, 0, 0],
       [0, 0, 0, ..., 1, 1, 0],
       [1, 1, 0, ..., 0, 1, 0],
       ...,
       [0, 1, 0, ..., 1, 1, 1],
       [1, 1, 1, ..., 0, 0, 1],
       [1, 1, 1, ..., 1, 1, 0]], shape=(30, 40))
>>> np.allclose(signal, inverted) # inverted signal matches signal
True

Installation
------------

intvert may be installed from `PyPI <https://pypi.org/project/intvert/>`_ with ``pip``.

.. code-block:: bash

       pip install intvert


References
----------
.. [LLL] Lenstra, A.K., Lenstra, H.W. & Lovász, L. Factoring polynomials with rational coefficients. Math. Ann. 261, 515–534 (1982). https://doi.org/10.1007/BF01457454
.. [LV] TODO
.. [PC] S. -C. Pei and K. -W. Chang, "Binary Signal Perfect Recovery From Partial DFT Coefficients," in IEEE Transactions on Signal Processing, vol. 70, pp. 3848-3861, 2022, doi: 10.1109/TSP.2022.3190615. 


Requirements
------------
intvert relies on the following Python packages:
 - `numpy <https://numpy.org/doc/stable/>`_ for fast array operations
 - `gmpy2 <https://gmpy2.readthedocs.io/en/stable/>`_ for multiple precision floating point operations
 - `fpylll <https://fpylll.readthedocs.io/en/stable/>`_ for implementations of the LLL lattice basis reduction algorithm
 - `sympy <https://docs.sympy.org/latest/index.html>`_ for integer factorization
