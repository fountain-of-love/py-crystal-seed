def greet() -> str:
    """
    Return the default greeting for the project.
    """
    return "{{cookiecutter.project_description}}"


def main() -> None:
    print(greet())


if __name__ == "__main__":
    main()
