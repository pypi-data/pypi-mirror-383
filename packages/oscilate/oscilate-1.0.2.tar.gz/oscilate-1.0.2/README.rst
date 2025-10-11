Nonlinear systems considered
==============================
The **OSCILATE** (Oscillators' nonlinear analysis through Symbolic ImplementATion of the mEthod of multiple scales) package allows the application of the **Method of Multiple Scales** (MMS) to a nonlinear equation or systems of :math:`N` coupled nonlinear equations of the form

.. math::
    \begin{cases}
            \ddot{x}_0 + \omega_0^2 x_0 & = f_0(\boldsymbol{x}, \dot{\boldsymbol{x}}, \ddot{\boldsymbol{x}}, t), \\
            & \vdots \\
            \ddot{x}_{N-1} + \omega_{N-1}^2 x_{N-1} & = f_{N-1}(\boldsymbol{x}, \dot{\boldsymbol{x}}, \ddot{\boldsymbol{x}}, t).
            \end{cases}

The :math:`x_i(t)` (:math:`i=0,...,N-1`) are the oscillators' coordinates, 

.. math::
    \boldsymbol{x}(t)^\intercal = [x_0(t), x_1(t), \cdots, x_{N-1}(t)]         


is the vector containing all the oscillators' coordinates (the :math:`^\intercal` denotes the transpose),
:math:`\omega_i` are their natural frequencies,
:math:`t` is the time and
:math:`\dot{(\bullet)} = \textrm{d}(\bullet)/\textrm{d}t` denotes a time-derivative.
The :math:`f_i` are functions which can contain:

- **Weak linear terms** in :math:`x_i,\; \dot{x}_i`, or :math:`\ddot{x}_i`.
- **Weak linear coupling terms** involving :math:`x_j,\; \dot{x}_j`, or :math:`\ddot{x}_j` with :math:`j \neq i`.
- **Weak nonlinear terms**. Taylor expansions are performed to approximate nonlinear terms as *polynomial nonlinearities*.
- **Forcing terms**:

  - Can be hard (appearing at leading order) or weak (small).
  - Primarily *harmonic*, e.g., :math:`F \cos(\omega t)`, where :math:`F` and :math:`\omega` are the forcing amplitude and frequency, respectively.
  - Modulated by any function (constant, linear, or nonlinear) to model *parametric* forcing (e.g., :math:`x_i(t) F \cos(\omega t)`).

Internal resonance relations among oscillators can be specified in a second step by expressing the :math:`\omega_i` as a function of a reference frequency.
Detuning can also be introduced during this step.

Overview
========
Solver
------
``MMS.py`` is the MMS solver. It contains 3 main classes:

- ``Dynamical_system`` : the dynamical system considered

- ``Multiple_scales_system`` : the system obtained after applying the MMS to the dynamical system

- ``Stead_state`` : the MMS results evaluated at steady state and (if computed) the system's response and its stability. 

These classes are described in details in the `documentation <https://vinceECN.github.io/OSCILATE/>`_.

Additional functions
--------------------
``sympy_functions.py`` contains additional functions that are not directly related to the MMS but which are used in ``MMS.py``.

Examples
--------
Application examples are proposed in the documentation. They include:

- The Duffing oscillator

- Coupled Duffing oscillators

- Coupled nonlinear oscillators with quadratic nonlinearities

- Parametrically excited oscillators

- Hard forcing of a Duffing oscillator

- Subharmonic response of 2 coupled centrifugal pendulum modes

Outputs
-------
Results are returned as sympy expressions.
They can be printed using LaTeX if the code is ran in an appropriate interactive Window. 
It is the case with VS Code's interactive Window or Spyder's IPython consol.

Here are possibilities:

- VS Code's interactive Window (powered by Jupyter)

- Jupyter notebook

- Spyder's IPython consol
 
Sympy expressions can also be printed as unformatted LaTeX using 

```
print(vlatex(the_expr))
```

Documentation
=============
A full `documentation <https://vinceECN.github.io/OSCILATE/>`_ is available.

Citation
========
Please cite this package when using it – see the CITATION file for details.

Installation guide
==================

Install from PyPI (recommended)
-------------------------------
To install the stable version from `PyPI <https://pypi.org/project/oscilate/>`_, use::

    pip install oscilate

Then, simply import the package in a python environment using::

    import oscilate


Install from a GitHub release
-----------------------------
To install from a GitHub release tagged as version `vX.Y.Z`, run::

    pip install https://github.com/vinceECN/OSCILATE/archive/refs/tags/vX.Y.Z.tar.gz



Install from the repository (latest version)
--------------------------------------------
To install the latest version directly from the GitHub repository, run::

    git clone https://github.com/vinceECN/OSCILATE.git
    cd OSCILATE
    pip install .


Dependencies
------------

- **Python 3.8 or higher** is required.

- For development or building documentation, install additional dependencies::
  
    pip install -r requirements-dev.txt
    pip install -r docs/requirements.txt
  

Optional: use a virtual environment (recommended)
-------------------------------------------------
To avoid conflicts with other packages, create and activate a virtual environment::

    python -m venv venv_mms
    source venv_mms/bin/activate   ## Linux/macOS
    .\venv_mms\Scripts\activate    ## Windows



Test the install
----------------

To test the install, follow these steps:

1. Open a python environment. Ideally one powered by Jupyter (see Outputs section) to display results as LaTeX.

2. In the documentation, go to *Application Examples/Example 1*. 

3. Copy the example code.

4. Run the example code in your python environment.

5. You should see information about the ongoing computations.

6. After the code is ran (a few seconds should be sufficient), figures of the forced response and its stability information are displayed.

7. To access the analytical solutions computed, type, for instance, ``ss.sol.fa``. They will be displayed as LaTeX if the python environment supports its. 


Disclaimer
==========
This code is provided as-is and has been tested on a limited number of nonlinear systems. 
Other test cases might trigger bugs or unexpected behavior that I am not yet aware of.
If you encounter any issues, find a bug, or have suggestions for improvements, please feel free to:
- Open an issue on the GitHub repository (if applicable).
- Propose a solution.
- Contact me directly at [vincent.mahe@ec-nantes.fr].

Your feedback is highly appreciated!

Vincent MAHE

License
=======
This project is licensed under the **Apache License 2.0** – see the LICENSE file for details.

