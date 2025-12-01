# Contributing & Release Guide

## Version Management

We use Semantic Versioning (Major.Minor.Patch). The version is defined in `pyproject.toml`.

### How to Release a New Version

1.  **Update Version**:
    Edit `pyproject.toml` and increment the version number.
    ```toml
    [project]
    version = "0.1.1"
    ```

2.  **Tag the Release**:
    Use the Makefile to tag the version in git.
    ```bash
    make tag-version v=0.1.1
    ```

3.  **Build and Publish**:
    You can use the Makefile to build and publish to PyPI.

    **TestPyPI (Recommended first):**
    ```bash
    make publish-test
    ```

    **PyPI (Production):**
    ```bash
    make publish
    ```

## Makefile Commands

-   `make install`: Install the package in editable mode.
-   `make test`: Run tests.
-   `make build`: Build the package (sdist and wheel).
-   `make clean`: Remove build artifacts.
-   `make publish-test`: Build and upload to TestPyPI.
-   `make publish`: Build and upload to PyPI.
