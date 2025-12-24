
import os
import sys
import argparse
from .tooling.config import ConfigLoader
from .tooling.builder import BuildSystem

def cmd_new(args):
    """Create a new NLPL project."""
    project_name = args.name
    if os.path.exists(project_name):
        print(f"Error: Directory '{project_name}' already exists.")
        return
    
    os.makedirs(project_name)
    os.makedirs(os.path.join(project_name, "src"))
    
    # Create nlpl.toml
    toml_content = f"""[package]
name = "{project_name}"
version = "0.1.0"
authors = []

[build]
source_dir = "src"
output_dir = "build"
target = "c"
optimization = 0
headers = false
"""
    with open(os.path.join(project_name, "nlpl.toml"), "w") as f:
        f.write(toml_content)
        
    # Create main.nlpl
    main_content = """
function main that takes nothing
    print "Hello, world!"
"""
    with open(os.path.join(project_name, "src", "main.nlpl"), "w") as f:
        f.write(main_content)
        
    print(f"Created new project: {project_name}")

def cmd_build(args):
    """Build the project."""
    try:
        config = ConfigLoader.load("nlpl.toml")
        builder = BuildSystem(config)
        if args.clean:
            builder.clean()
        # Pass optimization flag if present
        optimize_bounds = getattr(args, 'optimize_bounds_checks', False)
        builder.build(optimize_bounds_checks=optimize_bounds)
    except FileNotFoundError:
        print("Error: nlpl.toml not found. Are you in an NLPL project root?")
    except Exception as e:
        print(f"Error: {e}")

def cmd_run(args):
    """Build and run the project."""
    try:
        config = ConfigLoader.load("nlpl.toml")
        builder = BuildSystem(config)
        if builder.build():
            builder.run()
    except FileNotFoundError:
        print("Error: nlpl.toml not found. Are you in an NLPL project root?")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description="NLPL Compiler & Toolchain")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # new
    new_parser = subparsers.add_parser("new", help="Create a new project")
    new_parser.add_argument("name", help="Project name")
    
    # build
    build_parser = subparsers.add_parser("build", help="Build the project")
    build_parser.add_argument("--clean", action="store_true", help="Clean build directory first")
    build_parser.add_argument("--optimize-bounds-checks", action="store_true", 
                             help="Enable compile-time bounds check elimination")
    
    # run
    run_parser = subparsers.add_parser("run", help="Build and run the project")
    
    args = parser.parse_args()
    
    if args.command == "new":
        cmd_new(args)
    elif args.command == "build":
        cmd_build(args)
    elif args.command == "run":
        cmd_run(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
