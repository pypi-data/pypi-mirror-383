from .core.greet import greet
from .core.upflame_core import (
    initialize_project,
    run_diagnostics,
    process_data,
    pretty_print_diagnostics,
    pretty_print_project_init,
    generate_report
)
from .info.project_info import (
    get_project_name, 
    get_version, 
    get_author,
    get_description,
    get_license,
    get_python_version,
    get_project_url
)

__all__ = [
    "greet",
    "initialize_project",
    "run_diagnostics",
    "process_data",
    "pretty_print_diagnostics",
    "pretty_print_project_init",
    "generate_report",
    "get_project_name", 
    "get_version", 
    "get_author",
    "get_description",
    "get_license",
    "get_python_version",
    "get_project_url"
]