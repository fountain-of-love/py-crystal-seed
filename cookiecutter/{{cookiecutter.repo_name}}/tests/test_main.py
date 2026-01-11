from {{cookiecutter.package_name}}.main import greet


def test_greet_returns_project_description() -> None:
    assert greet() == "{{cookiecutter.project_description}}"
