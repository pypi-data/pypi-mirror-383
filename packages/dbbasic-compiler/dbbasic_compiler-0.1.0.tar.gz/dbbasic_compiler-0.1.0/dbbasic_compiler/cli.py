#!/usr/bin/env python3
"""
DBBasic-Compiler CLI

The command-line interface for the intelligent compiler.
"""

import sys
from .compiler import AICompiler


def main():
    """Main entry point for dbbasic-compile command."""
    if len(sys.argv) < 2:
        print("DBBasic-Compiler - The compiler that understands English")
        print()
        print("Usage:")
        print("  dbbasic-compile <intent_file>       # Compile intent to code")
        print("  dbbasic-compile run <program_name>  # Run compiled program")
        print("  dbbasic-compile list                # List compiled programs")
        print()
        print("Example:")
        print("  dbbasic-compile myapp.intent.md")
        print("  dbbasic-compile run myapp")
        print()
        print("Environment:")
        print("  ANTHROPIC_API_KEY must be set")
        print()
        print("Get your API key: https://console.anthropic.com/")
        return 1

    command = sys.argv[1]

    try:
        compiler = AICompiler()
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    # Handle 'list' command
    if command == "list":
        compiler.list_programs()
        return 0

    # Handle 'run' command
    if command == "run":
        if len(sys.argv) < 3:
            print("Usage: dbbasic-compile run <program_name>")
            return 1
        program_name = sys.argv[2]
        success = compiler.run(program_name)
        return 0 if success else 1

    # Otherwise treat first arg as intent file to compile
    intent_file = command
    success = compiler.compile(intent_file)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
