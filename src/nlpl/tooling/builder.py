
import os
import shutil
import glob
from typing import List
from .config import ProjectConfig
from ..compiler import Compiler, CompilerOptions, CompilationTarget
from ..parser.lexer import Lexer
from ..parser.parser import Parser

class BuildSystem:
    """Orchestrates the build process based on project configuration."""
    
    def __init__(self, config: ProjectConfig):
        self.config = config
        self.compiler = Compiler()
        self._configure_compiler()
        
    def _configure_compiler(self):
        """Configure compiler options from project config."""
        options = self.compiler.options
        options.optimization_level = self.config.build.optimization
        options.generate_header = self.config.build.headers
        # TODO: Add dependency paths to library search paths
        
    def clean(self):
        """Clean build directory."""
        if os.path.exists(self.config.build.output_dir):
            shutil.rmtree(self.config.build.output_dir)
            print(f"✓ Cleaned {self.config.build.output_dir}")
            
    def build(self) -> bool:
        """Build the project."""
        src_dir = self.config.build.source_dir
        out_dir = self.config.build.output_dir
        
        # Ensure output dir exists
        os.makedirs(out_dir, exist_ok=True)
        
        # Find all .nlpl files
        sources = glob.glob(os.path.join(src_dir, "**/*.nlpl"), recursive=True)
        
        if not sources:
            print(f"✗ No source files found in {src_dir}")
            return False
            
        print(f"Building {self.config.package.name} v{self.config.package.version}...")
        
        success_count = 0
        
        for source_path in sources:
            # Determine output path
            rel_path = os.path.relpath(source_path, src_dir)
            base_name = os.path.splitext(rel_path)[0]
            
            # If target is executable, output binary name depends on if it's main
            # For now, let's compile everything 
            # TODO: Handle multi-file modules properly. Currently compiling each file individually.
            
            output_file = os.path.join(out_dir, base_name)
            if self.config.build.target not in ["c", "cpp", "asm"]:
                # Append extension if not producing binary
                output_file += f".{self.config.build.target}"
            
            print(f"  Compiling {source_path}...")
            
            try:
                # Read source
                with open(source_path, 'r') as f:
                    code = f.read()
                
                # Parse
                lexer = Lexer(code)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()
                
                # Compile via Compiler class
                # Note: compile_and_link handles C/C++ linking to executable
                if self.config.build.target in [CompilationTarget.C, CompilationTarget.CPP]:
                     ok = self.compiler.compile_and_link(ast, self.config.build.target, output_file)
                else:
                     ok, _ = self.compiler.compile(ast, self.config.build.target, output_file)
                
                if ok:
                    success_count += 1
                else:
                    return False
                    
            except Exception as e:
                print(f"✗ Failed to compile {source_path}: {e}")
                import traceback
                traceback.print_exc()
                return False
                
        print(f"✓ Built {success_count} files to {out_dir}")
        return True

    def run(self):
        """Run the built executable."""
        # Find executable in build dir
        # Assuming usage of standard output name from build()
        # TODO: Better main entry point detection
        
        out_dir = self.config.build.output_dir
        # Try to find a file with no extension (binary) or main file
        
        # Simple heuristic: find the newest executable file or matching project name
        executable = os.path.join(out_dir, self.config.package.name)
        if not os.path.exists(executable):
            # Fallback: look for 'main'
            executable = os.path.join(out_dir, "main")
            
        if not os.path.exists(executable):
            # Fallback: find any executable
            import stat
            files = glob.glob(os.path.join(out_dir, "*"))
            for f in files:
                if os.access(f, os.X_OK) and not os.path.isdir(f) and not f.endswith(".o") and not f.endswith(".c"):
                    executable = f
                    break
        
        if os.path.exists(executable):
             print(f"Running {executable}...")
             os.system(executable)
        else:
             print("✗ No executable found to run")
