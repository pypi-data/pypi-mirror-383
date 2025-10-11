"""Test the no_op solver class."""

from ..no_op import NoOpSolver


def test_NoOpSolver():
    assert NoOpSolver.geometries() == []

    solver = NoOpSolver("no_geometry")
    assert solver.removeAllReflections() is None
    assert solver.refineLattice([]) is None
    assert solver.extra_axis_names == []
    assert solver.forward({}) == [{}]
    assert solver.inverse({}) == {}
    assert solver.calculate_UB(None, None) == []
    assert solver.addReflection(None) is None
