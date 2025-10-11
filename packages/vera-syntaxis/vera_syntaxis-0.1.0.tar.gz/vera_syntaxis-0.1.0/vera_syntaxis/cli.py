"""Command-line interface for Vera Syntaxis."""

import argparse
import logging
import sys
from pathlib import Path
from typing import List

from vera_syntaxis.file_discovery import discover_python_files
from vera_syntaxis.parser import ASTParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_parser() -> argparse.ArgumentParser:
    """
    Set up the command-line argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='vera-syntaxis',
        description='Static analysis tool for detecting architectural code smells in Python'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Parse command
    parse_parser = subparsers.add_parser(
        'parse',
        help='Parse Python files and display AST information'
    )
    parse_parser.add_argument(
        'project_path',
        type=Path,
        help='Path to the project directory to parse'
    )
    parse_parser.add_argument(
        '--dump-ast',
        action='store_true',
        help='Dump the full AST for each file'
    )
    
    # Analyze command (placeholder for Phase 3)
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze a project for architectural code smells (Phase 3)'
    )
    analyze_parser.add_argument(
        'project_path',
        type=Path,
        help='Path to the project directory to analyze'
    )
    
    return parser


def cmd_parse(args: argparse.Namespace) -> int:
    """
    Execute the parse command.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    project_path: Path = args.project_path
    
    logger.info(f"Parsing project: {project_path}")
    
    # Discover Python files
    try:
        python_files = discover_python_files(project_path)
    except ValueError as e:
        logger.error(f"Error discovering files: {e}")
        return 1
    
    if not python_files:
        logger.warning("No Python files found in project")
        return 0
    
    # Parse files
    parser = ASTParser()
    parsed_files = parser.parse_files(python_files)
    
    # Display results
    print(f"\n{'='*80}")
    print(f"Parse Results for: {project_path}")
    print(f"{'='*80}\n")
    
    print(f"Total files discovered: {len(python_files)}")
    print(f"Successfully parsed: {len(parsed_files)}")
    print(f"Parse errors: {len(parser.parse_errors)}")
    
    if parser.parse_errors:
        print(f"\n{'='*80}")
        print("Parse Errors:")
        print(f"{'='*80}\n")
        for error in parser.parse_errors:
            location = f"{error.file_path}"
            if error.line_number:
                location += f":{error.line_number}"
            print(f"  {location}")
            print(f"    {error.error_type}: {error.message}\n")
    
    if args.dump_ast:
        print(f"\n{'='*80}")
        print("AST Dumps:")
        print(f"{'='*80}\n")
        for file_path, parsed_file in parsed_files.items():
            print(f"\n{file_path}:")
            print("-" * 80)
            import ast
            print(ast.dump(parsed_file.ast_root, indent=2))
    
    # Display import information
    if parsed_files and not args.dump_ast:
        print(f"\n{'='*80}")
        print("Import Summary:")
        print(f"{'='*80}\n")
        for file_path, parsed_file in list(parsed_files.items())[:5]:  # Show first 5
            print(f"\n{file_path.name}:")
            import_map = parser.get_import_map(file_path)
            if import_map:
                for name, module in import_map.items():
                    print(f"  {name} -> {module}")
            else:
                print("  (no imports)")
        
        if len(parsed_files) > 5:
            print(f"\n  ... and {len(parsed_files) - 5} more files")
    
    return 0 if not parser.parse_errors else 1


def cmd_analyze(args: argparse.Namespace) -> int:
    """
    Execute the analyze command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for issues, 2 for violations found)
    """
    project_path: Path = args.project_path
    logger.info(f"Analyzing project: {project_path}")

    # 1. Load configuration
    from vera_syntaxis.config import load_config
    config = load_config(project_path)

    # 2. Discover and parse files
    try:
        python_files = discover_python_files(project_path)
    except ValueError as e:
        logger.error(f"Error discovering files: {e}")
        return 1
    
    if not python_files:
        logger.warning("No Python files found in project")
        return 0

    parser = ASTParser(project_path)
    parsed_files = parser.parse_files(python_files)
    if parser.parse_errors:
        logger.error("Encountered errors during parsing. Aborting analysis.")
        return 1

    # 3. Build Symbol Table
    from vera_syntaxis.symbol_table import SymbolTable, SymbolTableBuilder
    symbol_table = SymbolTable()
    for file_path, parsed_file in parsed_files.items():
        st_builder = SymbolTableBuilder(file_path, project_path, symbol_table)
        st_builder.visit(parsed_file.ast_root)

    # 4. Build Call Graph
    from vera_syntaxis.call_graph import build_call_graph
    call_graph = build_call_graph(parser, symbol_table, parsed_files)

    # 5. Run Linters
    from vera_syntaxis import linters  # This import is crucial to register the linters
    from vera_syntaxis.linter_base import LinterContext, run_all_linters
    context = LinterContext(config, parser, symbol_table, call_graph, parsed_files)
    violations = run_all_linters(context)

    # 6. Report Violations
    if violations:
        print(f"\n{'='*80}")
        print(f"Found {len(violations)} architectural violations:")
        print(f"{'='*80}\n")
        for violation in violations:
            print(f"- {violation}\n")
        return 2 # Indicate violations were found
    else:
        print("\nNo architectural violations found. Well done!")
        return 0


def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        Exit code
    """
    parser = setup_parser()
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Execute command
    if args.command == 'parse':
        return cmd_parse(args)
    elif args.command == 'analyze':
        return cmd_analyze(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
