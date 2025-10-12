#!/usr/bin/env python3
"""
Dana Command Line Interface - Main Entry Point

ARCHITECTURE ROLE:
    This is the PRIMARY ENTRY POINT for all Dana operations, analogous to the 'python' command.
    It acts as a ROUTER that decides whether to:
    - Execute a .na file directly (file mode)
    - Launch the Terminal User Interface (TUI mode)

USAGE PATTERNS:
    dana                 # Start TUI → delegates to tui_app.py
    dana script.na       # Execute file → uses DanaSandbox directly
    dana --help         # Show help and usage information

DESIGN DECISIONS:
    - Single entry point for all Dana operations (consistency)
    - File execution bypasses TUI overhead (performance)
    - TUI delegation to specialized interactive application (separation of concerns)
    - Console script integration via pyproject.toml (standard Python packaging)

INTEGRATION:
    - Console script: 'dana' command → this file's main() function
    - File execution: Uses DanaSandbox.quick_run() for direct .na file processing
    - TUI mode: Imports and delegates to tui_app.main() for interactive experience

This script serves as the main entry point for the Dana language, similar to the python command.
It either starts the TUI when no arguments are provided, or executes a .na file when given.

Usage:
  dana                         Start the Dana Terminal User Interface
  dana [file.na]               Execute a Dana file
  dana deploy [file.na]        Deploy a .na file as an agent endpoint
      [--protocol mcp|a2a|restful]  Protocol to use (default: restful)
      [--host HOST]            Host to bind the server (default: 0.0.0.0)
      [--port PORT]            Port to bind the server (default: 8000)
  dana studio                  Start the Dana Agent Studio
      [--host HOST]            Host to bind the server (default: 127.0.0.1)
      [--port PORT]            Port to bind the server (default: 8080)
      [--reload]               Enable auto-reload for development
      [--log-level LEVEL]      Log level (default: info)
  dana repl                    Start the Dana Interactive REPL
  dana tui                     Start the Dana Terminal User Interface
  dana -h, --help              Show help message
  dana --version               Show version information
  dana --debug                 Enable debug logging
  dana --no-color              Disable colored output
  dana --force-color           Force colored output

Examples:
  dana script.na               Execute a Dana script
  dana deploy agent.na         Deploy an agent
  dana deploy agent.na --protocol mcp --port 9000
  dana studio --port 9000      Start studio on port 9000
  dana repl                    Start interactive REPL
"""

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path

import uvicorn

# Set up compatibility layer for new dana structure
# Resolve the real path to avoid symlink issues
real_file = os.path.realpath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(real_file))))
sys.path.insert(0, project_root)

# Compatibility layer removed - direct Dana imports only

from dana.common.terminal_utils import ColorScheme, print_header, supports_color
from dana.common.utils.logging import DANA_LOGGER
from dana.core.lang.dana_sandbox import DanaSandbox
from dana.core.lang.log_manager import LogLevel, SandboxLogger

from .dana_input_args_parser import parse_dana_input_args

# Regex pattern to match "def __main__(" at the beginning of a line with zero whitespace before "def"
DEF_MAIN_PATTERN: re.Pattern = re.compile(r"^def\s+__main__\s*\(")
MAIN_FUNC_NAME: str = "__main__"

# Initialize color scheme
colors = ColorScheme(supports_color())


def show_help():
    """Display help information."""
    print(f"{colors.header('Dana - Domain-Aware NeuroSymbolic Architecture')}")
    print("")
    print(f"{colors.bold('Usage:')}")
    print(f"  {colors.accent('dana')}                   Start the Dana Terminal User Interface")
    print(f"  {colors.accent('dana [file.na]')}         Execute a Dana file")
    print(f"  {colors.accent('dana [file.na] [args]')}  Execute a Dana file with arguments (key=value)")
    print("")
    print(f"{colors.bold('Commands:')}")
    print(f"  {colors.accent('dana deploy [file.na]')}  Deploy a .na file as an agent endpoint")
    print(f"    {colors.accent('--protocol mcp|a2a|restful')}   Protocol to use (default: restful)")
    print(f"    {colors.accent('--host HOST')}          Host to bind the server (default: 0.0.0.0)")
    print(f"    {colors.accent('--port PORT')}          Port to bind the server (default: 8000)")
    print("")
    print(f"  {colors.accent('dana studio')}            Start the Dana Agent Studio")
    print(f"    {colors.accent('--host HOST')}          Host to bind the server (default: 127.0.0.1)")
    print(f"    {colors.accent('--port PORT')}          Port to bind the server (default: 8080)")
    print(f"    {colors.accent('--reload')}             Enable auto-reload for development")
    print(f"    {colors.accent('--log-level LEVEL')}    Log level (default: info)")
    print("")
    print(f"  {colors.accent('dana repl')}              Start the Dana Interactive REPL")
    print(f"  {colors.accent('dana tui')}               Start the Dana Terminal User Interface")
    print("")
    print(f"{colors.bold('Options:')}")
    print(f"  {colors.accent('dana -h, --help')}        Show this help message")
    print(f"  {colors.accent('dana --version')}         Show version information")
    print(f"  {colors.accent('dana --debug')}           Enable debug logging")
    print(f"  {colors.accent('dana --no-color')}        Disable colored output")
    print(f"  {colors.accent('dana --force-color')}     Force colored output")
    print("")
    print(f"{colors.bold('Examples:')}")
    print(f"  {colors.accent('dana script.na')}         Execute a Dana script")
    print(f"  {colors.accent('dana script.na key=value')}  Execute with arguments")
    print(f"  {colors.accent('dana deploy agent.na')}   Deploy an agent")
    print(f"  {colors.accent('dana studio --port 9000')}  Start studio on port 9000")
    print("")
    print(f"{colors.bold('Requirements:')}")
    print(f"  {colors.accent('🔑 API Keys:')} At least one LLM provider API key required")
    print("")
    print(f"{colors.bold('Script Arguments:')}")
    print(f"  {colors.accent('Format:')} key=value key2='quoted value' key3=@file.json")
    print(f"  {colors.accent('Files:')} Use @ prefix to load file contents (JSON, YAML, CSV, text)")
    print(f"  {colors.accent('Function:')} Arguments are passed to __main__() function if present")
    print("")


def execute_file(file_path, debug=False, script_args=None):
    """Execute a Dana file using the new DanaSandbox API."""
    # if developer puts an .env file in the script's directory, load it
    # Note: Environment loading is now handled automatically by initlib startup

    file_path_obj: Path = Path(file_path)

    print_header(f"Dana Execution: {file_path_obj.name}", colors=colors)

    source_code: str = file_path_obj.read_text(encoding="utf-8")

    if any(DEF_MAIN_PATTERN.search(line) for line in source_code.splitlines()):
        # Handle script arguments if provided
        input_dict = parse_dana_input_args(script_args) if script_args else {}

        # Append source code with main function call
        modified_source_code: str = f"""
{source_code}

{MAIN_FUNC_NAME}({", ".join([f"{key}={json.dumps(obj=value,
                                                 skipkeys=False,
                                                 ensure_ascii=False,
                                                 check_circular=True,
                                                 allow_nan=False,
                                                 cls=None,
                                                 indent=None,
                                                 separators=None,
                                                 default=None,
                                                 sort_keys=False)}"
                             for key, value in input_dict.items()])})
"""
    else:
        modified_source_code = source_code

    # Run the source code with custom search paths
    result = DanaSandbox.execute_string_once(
        source_code=modified_source_code,
        filename=str(file_path_obj),
        debug_mode=debug,
        module_search_paths=[str(file_path_obj.parent.resolve())],
    )

    if result.success:
        print(f"{colors.accent('Program executed successfully')}")

        # Show output if any
        if result.output:
            print(f"\n{colors.bold('Output:')}")
            print(result.output)

        # Show final context state
        print(f"\n{colors.bold('--- Final Context State ---')}")
        print(f"{colors.accent(str(result.final_context))}")
        print(f"{colors.bold('---------------------------')}")

        # Get final result if available
        if result.result is not None:
            print(f"\n{colors.bold('Result:')} {colors.accent(str(result.result))}")

        print(f"\n{colors.bold('✓ Program execution completed successfully')}")
    else:
        # Enhanced error display - show just the error message, not the full traceback
        error_msg = str(result.error)
        print(f"\n{colors.error('Error:')}")

        # Format the error message for display
        error_lines = error_msg.split("\n")
        for line in error_lines:
            if line.strip():
                print(f"  {line}")

        # In debug mode, also show the full traceback
        if debug:
            import traceback

            print(f"\n{colors.bold('Full traceback:')}")
            traceback.print_exc()

        sys.exit(1)


def start_repl():
    """Start the Dana REPL.

    ARCHITURAL NOTE: This function delegates to the full-featured interactive REPL application.
    It does NOT implement REPL logic itself - it imports and launches dana_repl_app.py which
    provides the complete interactive experience with commands, colors, multiline support, etc.
    """
    # Shift the repl subcommand from the argv
    if len(sys.argv) > 1 and sys.argv[1] == "repl":
        sys.argv = sys.argv[1:]

    # Import the REPL application module
    try:
        from dana.apps.repl.__main__ import main as repl_main

        repl_main()
    except ImportError as e:
        print(f"{colors.error(f'Error: Failed to import REPL module: {e}')}")
        sys.exit(1)
    except Exception as e:
        print(f"{colors.error(f'Error starting REPL: {e}')}")
        sys.exit(1)


def start_tui():
    """Start the Dana TUI.

    ARCHITECTURAL NOTE: This function delegates to the full-featured TUI application.
    It does NOT implement TUI logic itself - it imports and launches tui_app.py which
    provides the complete terminal user interface with panels, navigation, etc.
    """
    # Shift the tui subcommand from the argv
    if len(sys.argv) > 1 and sys.argv[1] == "tui":
        sys.argv = sys.argv[1:]

    # Import the TUI application module
    try:
        from dana.apps.tui.__main__ import main as tui_main

        tui_main()
    except ImportError as e:
        print(f"{colors.error(f'Error: Failed to import TUI module: {e}')}")
        sys.exit(1)
    except Exception as e:
        print(f"{colors.error(f'Error starting TUI: {e}')}")
        sys.exit(1)


def build_frontend():
    """Build the frontend by running npm install and npm run build.

    This function detects whether we're running from a pip installation
    (where frontend is pre-built) or a development installation (where
    we need to build it).
    """
    import subprocess
    import os

    try:
        # Check if we're running from a pip installation
        # Pip installations are located in site-packages, not in the current directory
        import dana

        is_pip_installation = "site-packages" in dana.__file__

        if is_pip_installation:
            # Running from pip installation - frontend is already built
            print(f"{colors.accent('✅ Using pre-built frontend from pip installation')}")
            return True

        # Development installation - need to build frontend
        # Get the project root directory (where we are now)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
        frontend_dir = os.path.join(project_root, "dana", "contrib", "ui")

        # Check if frontend directory exists
        if not os.path.exists(frontend_dir):
            print(f"{colors.error(f'❌ Frontend directory not found: {frontend_dir}')}")
            return False

        # Change to frontend directory and run npm install
        print(f"📦 Installing dependencies in {frontend_dir}...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, capture_output=True, text=True, check=True)
        print(f"{colors.accent('✅ Dependencies installed successfully')}")

        # Run npm run build
        print("🔨 Building frontend...")
        subprocess.run(["npm", "run", "build"], cwd=frontend_dir, capture_output=True, text=True, check=True)
        print(f"{colors.accent('✅ Frontend built successfully')}")

        return True

    except subprocess.CalledProcessError as e:
        print(f"{colors.error('❌ Frontend build failed:')}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"{colors.error('❌ npm command not found. Please ensure Node.js and npm are installed.')}")
        return False
    except Exception as e:
        print(f"{colors.error(f'❌ Unexpected error during frontend build: {str(e)}')}")
        return False


def handle_start_command(args):
    """Start the Dana API server using uvicorn."""
    try:
        # Build frontend before starting server
        print("\n🔨 Building frontend...")
        frontend_build_success = build_frontend()
        if not frontend_build_success:
            print(f"{colors.error('❌ Frontend build failed. Server startup aborted.')}")
            return 1

        # Start the server directly without configuration validation
        host = args.host or "127.0.0.1"
        port = args.port or 8080
        reload = args.reload
        log_level = args.log_level or "info"

        os.environ["STUDIO_RAG"] = "true"

        print(f"{colors.accent('✅ Enable STUDIO_RAG')}")

        print(f"\n🌐 Starting Dana API server on http://{host}:{port}")
        print(f"📊 Health check: http://{host}:{port}/health")
        print(f"🔗 Root endpoint: http://{host}:{port}/")

        uvicorn.run(
            "dana.api.server.server:create_app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            factory=True,
        )

    except Exception as e:
        print(f"{colors.error(f'❌ Server startup error: {str(e)}')}")
        return 1


def main():
    """Main entry point for the Dana CLI."""
    # if developer puts an .env file in the current working directory, load it
    # Note: Environment loading is now handled automatically by initlib startup

    args = None  # Initialize args to avoid unbound variable error
    try:
        parser = argparse.ArgumentParser(description="Dana Command Line Interface", add_help=False)
        parser.add_argument("--version", action="store_true", help="Show version information")
        subparsers = parser.add_subparsers(dest="subcommand")

        # Default/run subcommand (legacy behavior)
        parser_run = subparsers.add_parser("run", add_help=False)
        parser_run.add_argument("file", nargs="?", help="Dana file to execute (.na)")
        parser_run.add_argument("-h", "--help", action="store_true", help="Show help message")
        parser_run.add_argument("--version", action="store_true", help="Show version information")
        parser_run.add_argument("--no-color", action="store_true", help="Disable colored output")
        parser_run.add_argument("--force-color", action="store_true", help="Force colored output")
        parser_run.add_argument("--debug", action="store_true", help="Enable debug logging")

        # Deploy subcommand for single file
        parser_deploy = subparsers.add_parser("deploy", help="Deploy a .na file as an agent endpoint")
        parser_deploy.add_argument("file", help="Single .na file to deploy")
        parser_deploy.add_argument(
            "--protocol",
            choices=["mcp", "a2a", "restful"],
            default="restful",
            help="Protocol to use (default: restful)",
        )
        parser_deploy.add_argument(
            "--host",
            default="0.0.0.0",
            help="Host to bind the server (default: 0.0.0.0)",
        )
        parser_deploy.add_argument(
            "--port",
            type=int,
            default=8000,
            help="Port to bind the server (default: 8000)",
        )

        # Studio subcommand for Dana Agent Studio
        parser_studio = subparsers.add_parser("studio", help="Start the Dana Agent Studio")
        parser_studio.add_argument(
            "--host",
            default="127.0.0.1",
            help="Host to bind the server (default: 127.0.0.1)",
        )
        parser_studio.add_argument(
            "--port",
            type=int,
            default=8080,
            help="Port to bind the server (default: 8080)",
        )
        parser_studio.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
        parser_studio.add_argument("--log-level", default="info", help="Log level (default: info)")

        # TUI subcommand for terminal user interface
        parser_tui = subparsers.add_parser("tui", help="Start the Dana Terminal User Interface")
        parser_tui.add_argument("--debug", action="store_true", help="Enable debug logging")

        # REPL subcommand for interactive REPL
        parser_repl = subparsers.add_parser("repl", help="Start the Dana Interactive REPL")
        parser_repl.add_argument("--debug", action="store_true", help="Enable debug logging")

        # Handle default behavior
        if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] not in ("deploy", "studio", "tui", "repl")):
            return handle_main_command()

        # Parse subcommand
        args = parser.parse_args()

        # Show version if requested
        if args.version:
            from dana import __version__

            print(f"Dana {__version__}")
            return 0

        if args.subcommand == "deploy":
            return handle_deploy_command(args)
        elif args.subcommand == "studio":
            return handle_start_command(args)
        elif args.subcommand == "tui":
            return start_tui()
        elif args.subcommand == "repl":
            return start_repl()

        return 0

    except KeyboardInterrupt:
        print("\nDANA execution interrupted by user")
        return 0
    except Exception as e:
        print(f"\n{colors.error(f'Unexpected error: {str(e)}')}")
        if args and hasattr(args, "debug") and args.debug:
            import traceback

            traceback.print_exc()
        return 1


def handle_main_command():
    """Handle main Dana command line behavior (run files or start REPL)."""
    parser = argparse.ArgumentParser(description="Dana Command Line Interface", add_help=False)
    parser.add_argument("file", nargs="?", help="Dana file to execute (.na)")
    parser.add_argument("-h", "--help", action="store_true", help="Show help message")
    parser.add_argument("--version", action="store_true", help="Show version information")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("--force-color", action="store_true", help="Force colored output")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("script_args", nargs=argparse.REMAINDER, help="Script arguments as key=value pairs")

    args = parser.parse_args()

    # Handle color settings
    global colors
    if args.no_color:
        colors = ColorScheme(False)
    elif args.force_color:
        colors = ColorScheme(True)

    # Configure debug logging
    if args.debug:
        configure_debug_logging()

    # Show version if requested
    if args.version:
        from dana import __version__

        print(f"Dana {__version__}")
        return 0

    # Show help if requested
    if args.help:
        show_help()
        return 0

    # Handle file execution or TUI
    if args.file:
        if not validate_na_file(args.file):
            return 1
        execute_file(args.file, debug=args.debug, script_args=args.script_args)
    else:
        start_tui()

    return 0


def handle_deploy_command(args):
    """Handle the deploy subcommand."""
    try:
        # Validate the file
        if not validate_na_file(args.file):
            return 1

        if not os.path.isfile(args.file):
            print(f"{colors.error(f'Error: File {args.file} does not exist')}")
            return 1

        file_path = os.path.abspath(args.file)

        if args.protocol == "mcp":
            return deploy_thru_mcp(file_path, args)
        elif args.protocol == "a2a":
            return deploy_thru_a2a(file_path, args)
        else:  # restful
            return deploy_thru_restful(file_path, args)

    except Exception as e:
        print(f"\n{colors.error(f'Deploy command error: {str(e)}')}")
        if hasattr(args, "debug") and args.debug:
            import traceback

            traceback.print_exc()
        return 1


def deploy_thru_mcp(file_path, args):
    """Deploy file using MCP protocol."""
    try:
        from dana.apps.cli.deploy.mcp import deploy_dana_agents_thru_mcp

        deploy_dana_agents_thru_mcp(file_path, args.host, args.port)
        return 0
    except ImportError as e:
        print(f"\n{colors.error('Error: Required packages missing')}")
        print(f"{colors.bold(f'Please install required packages: {e}')}")
        return 1
    except Exception as e:
        print(f"\n{colors.error('MCP Server Error:')}")
        print(f"  {str(e)}")
        return 1


def deploy_thru_a2a(file_path, args):
    """Deploy file using A2A protocol."""
    try:
        from dana.apps.cli.deploy.a2a import deploy_dana_agents_thru_a2a

        deploy_dana_agents_thru_a2a(file_path, args.host, args.port)
        return 0
    except Exception as e:
        print(f"\n{colors.error('A2A Server Error:')}")
        print(f"  {str(e)}")
        return 1


def deploy_thru_restful(file_path, args):
    """Deploy file using RESTful API protocol."""
    try:
        from dana.apps.cli.deploy.restapi import deploy_dana_agent_rest_api

        deploy_dana_agent_rest_api(file_path, args.host, args.port)
        return 0
    except ImportError as e:
        print(f"\n{colors.error('Error: Required packages missing')}")
        print(f"{colors.bold(f'Please install required packages: {e}')}")
        return 1
    except Exception as e:
        print(f"\n{colors.error('RESTful API Server Error:')}")
        print(f"  {str(e)}")
        return 1


def configure_debug_logging():
    """Configure debug logging settings."""
    print(f"{colors.accent('Debug logging enabled')}")
    DANA_LOGGER.configure(level=logging.DEBUG, console=True)
    SandboxLogger.set_system_log_level(LogLevel.DEBUG)


def validate_na_file(file_path):
    """Validate that the file exists and has .na extension."""
    if not file_path.endswith(".na"):
        print(f"{colors.error('Error: File must have .na extension')}")
        print("")
        show_help()
        return False
    return True


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDANA execution interrupted by user")
        sys.exit(0)
