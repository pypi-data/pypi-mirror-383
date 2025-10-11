from . import (
    greet, 
    get_author, 
    get_project_name, 
    get_version,
    get_description,
    initialize_project,
    run_diagnostics,
    pretty_print_project_init,
    pretty_print_diagnostics
)

def main():
    print("=== Project Info ===")
    print(f"Project Name: {get_project_name()}")
    print(f"Version: {get_version()}")
    print(f"Author: {get_author()}")
    print(f"Description: {get_description()}")
    
    print("\n=== Greet Example ===")
    print(greet("Victor"))
    
    print("\n=== Project Initialization Demo ===")
    project = initialize_project("Sample Project", "web")
    pretty_print_project_init(project)
    
    print("\n=== System Diagnostics Demo ===")
    diagnostics = run_diagnostics()
    pretty_print_diagnostics(diagnostics)

if __name__ == "__main__":
    main()