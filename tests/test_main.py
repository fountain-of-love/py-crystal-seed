from py_crystal_seed.main import greet


def test_greet() -> None:
    assert greet() == "The seed has structure."
