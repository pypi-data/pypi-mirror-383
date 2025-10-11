"""
Abstract base class for all solvers.

.. autosummary::

    ~SolverBase
"""

import logging
from abc import ABC
from abc import abstractmethod
from typing import Dict

from pyRestTable import Table

from ..misc import IDENTITY_MATRIX_3X3
from ..misc import INTERNAL_ANGLE_UNITS
from ..misc import INTERNAL_LENGTH_UNITS
from ..misc import istype
from ..misc import validate_and_canonical_unit

logger = logging.getLogger(__name__)

Lattice = Dict[str, float]
Reflection = Dict[str, object]
Sample = Dict[str, object]


class SolverBase(ABC):
    """
    Base class for all |hklpy2| |solver| classes.

    PARAMETERS

    geometry : str
        Name of geometry.
    mode: str
        Name of operating mode.  (default: current mode)

    Example::

        import hklpy2

        class MySolver(hklpy2.SolverBase):
            ...

    .. note:: :class:`~SolverBase`, an `abstract base
        class <https://docs.python.org/3/library/abc.html#abc.ABC>`_,
        cannot not be used directly by |hklpy2| users.

    As the parent class for all custom :index:`Solver` classes,
    :class:`~SolverBase` defines the methods and attributes to be written
    that will connect |hklpy2| with the support library that defines
    specific diffractometer geometries and the computations for
    using them.  Subclasses should implement each of these methods
    as best fits the underlying support library.

    .. seealso:: :mod:`~hklpy2.backends.hkl_soleil` & :mod:`~hklpy2.backends.no_op`

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

        ~all_extra_axis_names
        ~extra_axis_names
        ~extras
        ~geometry
        ~lattice
        ~mode
        ~modes
        ~sample
        ~UB
    """

    from .. import __version__

    name = "base"
    """Name of this Solver."""

    version = __version__
    """Version of this Solver."""

    ANGLE_UNITS = "degrees"
    """
    Angle units used by this solver for unit cell and real axis rotations.

    Solver can override this **constant**.  Must be convertible to
    ``INTERNAL_ANGLE_UNITS``.
    """

    LENGTH_UNITS = "angstrom"
    """
    Length units used by this solver for unit cell and wavelength.

    Solver can override this **constant**.  Must be convertible to
    ``INTERNAL_LENGTH_UNITS``.
    """

    def __init__(
        self,
        geometry: str,
        *,
        mode: str = "",  # "": accept solver's default mode
        **kwargs,
    ) -> None:
        self._gname = geometry
        self.mode = mode
        self._all_extra_axis_names = None
        self._sample = None

        validate_and_canonical_unit(self.ANGLE_UNITS, INTERNAL_ANGLE_UNITS)
        validate_and_canonical_unit(self.LENGTH_UNITS, INTERNAL_LENGTH_UNITS)

        logger.debug("geometry=%s, kwargs=%s", repr(geometry), repr(kwargs))

    def __repr__(self) -> str:
        # fmt: off
        args = [
            f"{s}={getattr(self, s)!r}"
            for s in "name version geometry".split()
        ]
        # fmt: on
        return f"{self.__class__.__name__}({', '.join(args)})"

    @property
    def _metadata(self) -> dict:
        """Dictionary with this solver's summary metadata."""
        return {
            "name": self.name,
            "description": repr(self),
            "geometry": self.geometry,
            "real_axes": self.real_axis_names,
            "version": self.version,
        }

    @abstractmethod
    def addReflection(self, reflection: Reflection) -> None:
        """Add coordinates of a diffraction condition (a reflection)."""

    @property
    def all_extra_axis_names(self) -> list[str]:
        """Unique, sorted list of extra axis names in all modes for chosen engine."""
        if self._all_extra_axis_names is None:
            # Only collect this once.
            original = self.mode
            names = []
            for mode in self.modes:
                self.mode = mode
                names += self.extra_axis_names
            self.mode = original  # put it back
            self._all_extra_axis_names = sorted(list(set(names)))
        return self._all_extra_axis_names

    @abstractmethod
    def calculate_UB(
        self,
        r1: Reflection,
        r2: Reflection,
    ) -> list[list[float]]:
        """
        Calculate the UB (orientation) matrix with two reflections.

        The method of Busing & Levy, Acta Cryst 22 (1967) 457.
        """
        # return self.UB

    @property
    @abstractmethod
    def extra_axis_names(self) -> list[str]:
        """Ordered list of any extra axis names (such as x, y, z)."""
        # Do NOT sort.
        # return []

    @property
    def extras(self) -> dict:
        """
        Ordered dictionary of any extra parameters.
        """
        return {}

    @abstractmethod
    def forward(self, pseudos: dict) -> list[dict[str, float]]:
        """Compute list of solutions(reals) from pseudos (hkl -> [angles])."""
        # based on geometry and mode
        # return [{}]

    @classmethod
    @abstractmethod
    def geometries(cls) -> list[str]:
        """
        Ordered list of the geometry names.

        EXAMPLES::

            >>> from hklpy2 import get_solver
            >>> Solver = get_solver("no_op")
            >>> Solver.geometries()
            []
            >>> solver = Solver("TH TTH Q")
            >>> solver.geometries()
            []
        """
        # return []

    @property
    def geometry(self) -> str:
        """
        Name of selected diffractometer geometry.

        Cannot be changed once solver is created.  Instead, make a new solver
        for each geometry.
        """
        return self._gname

    @abstractmethod
    def inverse(self, reals: dict) -> dict[str, float]:
        """Compute dict of pseudos from reals (angles -> hkl)."""
        # return {}

    @property
    def lattice(self) -> Lattice:
        """
        Crystal lattice parameters.  (Not used by this |solver|.)
        """
        return self._lattice

    @lattice.setter
    def lattice(self, value: Lattice):
        if not istype(value, Lattice):
            raise TypeError(f"Must supply {Lattice} object, received {value!r}")
        self._lattice = value

    @property
    def mode(self) -> str:
        """
        Diffractometer geometry operation mode for :meth:`forward()`.

        A mode defines which axes will be modified by the
        :meth:`forward` computation.
        """
        try:
            self._mode
        except AttributeError:
            self._mode = ""
        return self._mode

    @mode.setter
    def mode(self, value: str):
        from ..misc import check_value_in_list  # avoid circular import here

        check_value_in_list("Mode", value, self.modes, blank_ok=True)
        self._mode = value

    @property
    @abstractmethod
    def modes(self) -> list[str]:
        """List of the geometry operating modes."""
        # return []

    @property
    @abstractmethod
    def pseudo_axis_names(self) -> list[str]:
        """Ordered list of the pseudo axis names (such as h, k, l)."""
        # Do NOT sort.
        # return []

    @property
    @abstractmethod
    def real_axis_names(self) -> list[str]:
        """Ordered list of the real axis names (such as th, tth)."""
        # Do NOT sort.
        # return []

    @abstractmethod
    def refineLattice(self, reflections: list[Reflection]) -> Lattice:
        """Refine the lattice parameters from a list of reflections."""

    @abstractmethod
    def removeAllReflections(self) -> None:
        """Remove all reflections."""

    @property
    def sample(self) -> object:
        """
        Crystalline sample.
        """
        return self._sample

    @sample.setter
    def sample(self, value: Sample):
        if not istype(value, Sample):
            raise TypeError(f"Must supply {Sample} object, received {value!r}")
        self._sample = value

    @property
    def _summary_dict(self):
        """Return a summary of the geometry (modes, axes)"""
        geometry_name = self.geometry
        description = {
            "name": geometry_name,
            "pseudos": self.pseudo_axis_names,
            "reals": self.real_axis_names,
            "modes": {},
        }

        for mode in self.modes:
            self.mode = mode
            desc = {
                "extras": [],
                # the reals to be written in this mode (solver should override)
                "reals": self.real_axis_names,
            }
            description["modes"][mode] = desc

        return description

    @property
    def summary(self) -> Table:
        """
        Table of this geometry (modes, axes).

        .. seealso:: :ref:`geometries.summary_tables`,
            :func:`hklpy2.user.solver_summary()`
        """
        table = Table()
        table.labels = "mode pseudo(s) real(s) writable(s) extra(s)".split()
        sdict = self._summary_dict
        for mode_name, mode in sdict["modes"].items():
            self.mode = mode_name
            row = [
                mode_name,
                ", ".join(sdict["pseudos"]),
                ", ".join(sdict["reals"]),
                ", ".join(mode["reals"]),
                ", ".join(mode["extras"]),
            ]
            table.addRow(row)
        return table

    @property
    def UB(self):
        """Orientation matrix (3x3)."""
        return IDENTITY_MATRIX_3X3
