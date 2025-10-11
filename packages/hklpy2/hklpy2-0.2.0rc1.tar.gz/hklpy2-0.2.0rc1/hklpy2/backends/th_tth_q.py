"""
"th_tth" example solver in Python.

Transformations between :math:`\\theta,2\\theta` and :math:`Q`.

Example::

    import hklpy2
    SolverClass = hklpy2.get_solver("th_tth")
    solver = SolverClass()

.. autosummary::

    ~ThTthSolver
"""

import logging
import math

from .. import __version__
from ..blocks.reflection import Reflection
from ..misc import SolverError
from .base import SolverBase

logger = logging.getLogger(__name__)
TH_TTH_Q_GEOMETRY = "TH TTH Q"
TH_Q_GEOMETRY = "TH Q"  # TODO: Second geometry?
BISECTOR_MODE = "bissector"  # spelled same as in E4CV


class ThTthSolver(SolverBase):
    """
    ``"th_tth"`` (any OS) :math:`\\theta,2\\theta` and :math:`Q`.

    ============== =================
    transformation equation
    ============== =================
    ``forward()``  :math:`\\theta = \\sin^{-1}(q\\lambda / 4\\pi)`
    ``inverse()``  :math:`q = (4\\pi / \\lambda) \\sin(\\theta)`
    ============== =================

    Wavelength is specified either directly (``solver.wavelength = 1.0``) or
    by adding at least one :index:`reflection` (see
    :class:`~hklpy2.blocks.reflection.Reflection`).  All
    reflections must have the same :index:`wavelength`.

    No orientation matrix is used in this geometry.

    .. rubric:: Python Methods

    .. autosummary::

        ~addReflection
        ~calculate_UB
        ~extra_axis_names
        ~forward
        ~geometries
        ~inverse
        ~pseudo_axis_names
        ~real_axis_names
        ~refineLattice
        ~removeAllReflections

    .. rubric:: Python Properties

    .. autosummary::

        ~geometry
        ~lattice
        ~mode
        ~modes
        ~sample
    """

    name = "th_tth"
    version = __version__

    def __init__(self, geometry: str, **kwargs) -> None:
        super().__init__(geometry, **kwargs)
        self._reflections = []
        self._wavelength = None

    def addReflection(self, value: Reflection):
        """Add coordinates of a diffraction condition (a reflection)."""
        if not isinstance(value, Reflection):
            raise TypeError(f"Must supply Reflection object, received {value!r}")
        self._reflections.append(value)

        # validate: all reflections must have same wavelength
        wavelengths = [r.wavelength for r in self._reflections]
        if min(wavelengths) != max(wavelengths):
            self._reflections.pop(-1)
            raise SolverError(
                f"All reflections must have same wavelength. Received: {wavelengths!r}"
            )
        self.wavelength = wavelengths[0]

    def calculate_UB(self, r1, r2):
        return []

    def forward(self, pseudos: dict) -> list[dict[str, float]]:
        """Transform pseudos to list of reals."""
        if not isinstance(pseudos, dict):
            raise TypeError(f"Must supply dict, received {pseudos!r}")

        solutions = []
        if self.geometry == TH_TTH_Q_GEOMETRY:
            q = pseudos.get("q")
            if q is None:
                raise SolverError(f"'q' not defined. Received {pseudos!r}.")
            if self.wavelength is None:
                raise SolverError("Wavelength is not set. Add a reflection.")
            if self.mode == BISECTOR_MODE:
                th = math.degrees(math.asin(q * self.wavelength / 4 / math.pi))
                solutions.append({"th": th, "tth": 2 * th})

        return solutions

    @property
    def extra_axis_names(self):
        return []

    @classmethod
    def geometries(cls):
        return [TH_TTH_Q_GEOMETRY]  # only one geometry

    def inverse(self, reals: dict):
        """Transform reals to pseudos."""
        if not isinstance(reals, dict):
            raise TypeError(f"Must supply dict, received {reals!r}")

        pseudos = {}
        if self.geometry == TH_TTH_Q_GEOMETRY:
            tth = reals.get("tth")
            if tth is None:
                raise SolverError(f"'tth' not defined. Received {reals!r}.")
            if self.wavelength is None:
                raise SolverError("Wavelength is not set. Add a reflection.")
            if self.mode == BISECTOR_MODE:
                q = (4 * math.pi) / self.wavelength
                q *= math.sin(math.radians(tth / 2))
                pseudos["q"] = q
        return pseudos

    @property
    def modes(self):
        if self.geometry == TH_TTH_Q_GEOMETRY:
            return [BISECTOR_MODE]

    @property
    def pseudo_axis_names(self):
        axes = {TH_TTH_Q_GEOMETRY: ["q"]}
        return axes.get(self.geometry, [])

    @property
    def real_axis_names(self):
        axes = {TH_TTH_Q_GEOMETRY: "th tth".split()}
        return axes.get(self.geometry, [])

    def refineLattice(self, reflections: list[Reflection]) -> None:
        """No lattice refinement in this |solver|."""
        return None

    def removeAllReflections(self):
        """Remove all reflections."""
        raise NotImplementedError()  # TODO: implement this method

    @property
    def wavelength(self):
        """Diffractometer wavelength, for forward() and inverse()."""
        return self._wavelength

    @wavelength.setter
    def wavelength(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"Must supply number, received {value!r}")
        if value <= 0:
            raise ValueError(f"Must supply positive number, received {value!r}")
        self._wavelength = value
