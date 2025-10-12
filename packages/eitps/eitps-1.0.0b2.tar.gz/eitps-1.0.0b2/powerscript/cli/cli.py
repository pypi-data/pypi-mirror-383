"""
MIT License

Copyright (c) 2025 Saleem Ahmad (Elite India Org Team)
Email: team@eliteindia.org

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import argparse
import sys
import os
from typing import List, Optional
from .commands import CompileCommand, RunCommand, CreateCommand, CheckCommand


class CLI:
    """Main CLI class for PowerScript"""
    
    def __init__(self):
        self.parser = self._create_parser()
        self.commands = {
            'compile': CompileCommand(),
            'run': RunCommand(),
            'create': CreateCommand(),
            'check': CheckCommand()
        }
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser"""
        parser = argparse.ArgumentParser(
            prog='tps',
            description='PowerScript (TPS) - A fully structured development language that transpiles to Python',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Commands:
  compile (c)     Compile TPS files to Python
  run (r)         Run TPS files directly
  create          Create a new TPS project
  check           Run type checker on TPS files

Examples:
  tps compile src/ -o build/
  tps run src/main.ps
  tps create my_project
  tps check src/
  
Easy Commands:
  tps-compile file.ps    # Direct compile
  tps-run file.ps        # Direct run
  tps-create project     # Direct create
  ps file.ps             # Quick run (alias)
            """
        )
        
        parser.add_argument(
            '--version', '-v',
            action='version',
            version='PowerScript (TPS) 1.0.0'
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Compile command
        compile_parser = subparsers.add_parser(
            'compile', aliases=['c'],
            help='Compile PowerScript files to Python'
        )
        compile_parser.add_argument(
            'source',
            help='Source file or directory to compile'
        )
        compile_parser.add_argument(
            '-o', '--output',
            default='build/',
            help='Output directory (default: build/)'
        )
        compile_parser.add_argument(
            '-w', '--watch',
            action='store_true',
            help='Watch for file changes and recompile'
        )
        compile_parser.add_argument(
            '--strict',
            action='store_true',
            help='Enable strict type checking'
        )
        compile_parser.add_argument(
            '--no-runtime-checks',
            action='store_true',
            help='Disable runtime type checks'
        )
        compile_parser.add_argument(
            '--generate-stubs',
            action='store_true',
            help='Generate .pyi stub files'
        )
        
        # Run command
        run_parser = subparsers.add_parser(
            'run', aliases=['r'],
            help='Run PowerScript files directly'
        )
        run_parser.add_argument(
            'file',
            help='PowerScript file to run'
        )
        run_parser.add_argument(
            'args',
            nargs='*',
            help='Arguments to pass to the script'
        )
        run_parser.add_argument(
            '--no-cache',
            action='store_true',
            help='Don\'t use cached compiled files'
        )
        
        # Create command
        create_parser = subparsers.add_parser(
            'create',
            help='Create a new PowerScript project'
        )
        create_parser.add_argument(
            'name',
            help='Project name'
        )
        create_parser.add_argument(
            '--template',
            choices=['basic', 'ai', 'web', 'cli'],
            default='basic',
            help='Project template (default: basic)'
        )
        create_parser.add_argument(
            '--no-git',
            action='store_true',
            help='Don\'t initialize git repository'
        )
        
        # Check command
        check_parser = subparsers.add_parser(
            'check',
            help='Run type checker on PowerScript files'
        )
        check_parser.add_argument(
            'source',
            help='Source file or directory to check'
        )
        check_parser.add_argument(
            '--strict',
            action='store_true',
            help='Enable strict type checking'  
        )
        check_parser.add_argument(
            '--json',
            action='store_true',
            help='Output results in JSON format'
        )
        
        return parser
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI with given arguments"""
        if args is None:
            args = sys.argv[1:]
        
        try:
            parsed_args = self.parser.parse_args(args)
            
            if not parsed_args.command:
                self.parser.print_help()
                return 1
            
            # Map aliases to full command names
            command_name = parsed_args.command
            if command_name == 'c':
                command_name = 'compile'
            elif command_name == 'r':
                command_name = 'run'
            
            command = self.commands.get(command_name)
            if not command:
                print(f"Unknown command: {command_name}", file=sys.stderr)
                return 1
            
            return command.execute(parsed_args)
            
        except KeyboardInterrupt:
            print("\nOperation cancelled by user", file=sys.stderr)
            return 130
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1


def main() -> int:
    """Main entry point for PowerScript CLI"""
    cli = CLI()
    return cli.run()


# Entry points for different commands
def powerscriptc_main() -> int:
    """Entry point for powerscriptc command"""
    sys.argv[0] = 'powerscriptc'
    args = ['compile'] + sys.argv[1:]
    cli = CLI()
    return cli.run(args)


def ps_run_main() -> int:
    """Entry point for ps-run command"""
    sys.argv[0] = 'ps-run'
    args = ['run'] + sys.argv[1:]
    cli = CLI()
    return cli.run(args)


def ps_create_main() -> int:
    """Entry point for ps-create command"""
    sys.argv[0] = 'ps-create'
    args = ['create'] + sys.argv[1:]
    cli = CLI()
    return cli.run(args)


def psc_main() -> int:
    """Entry point for psc (type checker) command"""
    sys.argv[0] = 'psc'
    args = ['check'] + sys.argv[1:]
    cli = CLI()
    return cli.run(args)


# New simplified TPS command entry points
def compile_command() -> int:
    """Direct compile command: tps-compile file.ps"""
    if len(sys.argv) < 2:
        print("Usage: tps-compile <file.ps>", file=sys.stderr)
        return 1
    
    args = ['compile'] + sys.argv[1:]
    cli = CLI()
    try:
        return cli.run(args)
    except Exception as e:
        print(f"❌ Compilation Error: {e}", file=sys.stderr)
        return 1


def run_command() -> int:
    """Direct run command: tps-run file.ps"""
    if len(sys.argv) < 2:
        print("Usage: tps-run <file.ps>", file=sys.stderr)
        return 1
    
    args = ['run'] + sys.argv[1:]
    cli = CLI()
    try:
        return cli.run(args)
    except Exception as e:
        print(f"❌ Runtime Error: {e}", file=sys.stderr)
        return 1


def create_command() -> int:
    """Direct create command: tps-create project_name"""
    if len(sys.argv) < 2:
        print("Usage: tps-create <project_name>", file=sys.stderr)
        return 1
    
    args = ['create'] + sys.argv[1:]
    cli = CLI()
    try:
        return cli.run(args)
    except Exception as e:
        print(f"❌ Project Creation Error: {e}", file=sys.stderr)
        return 1


def ps_smart_command() -> int:
    """Smart PS command - runs file if provided, otherwise compiles all .ps files"""
    if len(sys.argv) >= 2 and sys.argv[1].endswith('.ps'):
        # If a .ps file is provided, run it
        return run_command()
    else:
        # Otherwise, do smart compilation
        return smart_compile()


def smart_compile() -> int:
    """Smart compilation - automatically detects .ps files and compiles them"""
    import glob
    import os
    
    # Find all .ps files in current directory and subdirectories
    ps_files = glob.glob("**/*.ps", recursive=True)
    
    if not ps_files:
        print("No .ps files found in current directory.", file=sys.stderr)
        return 1
    
    print(f"🔍 Found {len(ps_files)} PowerScript files:")
    for file in ps_files:
        print(f"  📄 {file}")
    
    cli = CLI()
    failed_files = []
    
    for ps_file in ps_files:
        try:
            print(f"\n🔨 Compiling {ps_file}...")
            result = cli.run(['compile', ps_file])
            if result != 0:
                failed_files.append(ps_file)
                print(f"❌ Failed to compile {ps_file}")
            else:
                print(f"✅ Successfully compiled {ps_file}")
        except Exception as e:
            failed_files.append(ps_file)
            print(f"❌ Error compiling {ps_file}: {e}")
    
    if failed_files:
        print(f"\n❌ Compilation failed for {len(failed_files)} files:")
        for file in failed_files:
            print(f"  📄 {file}")
        return 1
    else:
        print(f"\n🎉 Successfully compiled all {len(ps_files)} PowerScript files!")
        return 0


if __name__ == '__main__':
    sys.exit(main())