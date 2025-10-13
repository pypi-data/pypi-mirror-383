"""General utility functions, should not import anything from rthor."""

from __future__ import annotations

import importlib.util


def is_running_in_ipynb() -> bool:
    """Check if the code is running in a Jupyter notebook."""
    try:
        from IPython.core.getipython import get_ipython  # noqa: PLC0415
    except ImportError:
        return False
    try:
        return get_ipython().__class__.__name__ == "ZMQInteractiveShell"  # type: ignore[name-defined]
    except NameError:
        return False  # Probably standard Python interpreter


def is_installed(package: str) -> bool:
    """Check if a package is installed."""
    return importlib.util.find_spec(package) is not None


def requires(*packages: str, reason: str = "", extras: str | None = None) -> None:
    """Check if a package is installed, raise an ImportError if not."""
    conda_name_mapping = {
        "graphviz": "python-graphviz",
        "graphviz_anywidget": "graphviz-anywidget",
    }

    for package in packages:
        if is_installed(package):
            continue
        conda_package = conda_name_mapping.get(package, package)
        error_message = f"The '{package}' package is required"
        if reason:
            error_message += f" for {reason}"
        error_message += ".\n"
        error_message += "Please install it using one of the following methods:\n"
        if extras:
            error_message += f'- pip install "pipefunc[{extras}]"\n'
        error_message += f"- pip install {package}\n"
        error_message += f"- conda install -c conda-forge {conda_package}"
        raise ImportError(error_message)
