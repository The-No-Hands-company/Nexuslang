
import os
import shutil
import glob
from typing import List, Optional, Dict
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
        
        # Add dependency paths to library search paths
        # Dependencies are typically installed in standard locations or specified paths
        for dep_name, dep_spec in self.config.dependencies.items():
            # If dependency specifies a path (local dependency)
            if isinstance(dep_spec, dict) and 'path' in dep_spec:
                dep_path = dep_spec['path']
                # Add the dependency's build/lib directory to search paths
                lib_path = os.path.join(dep_path, 'build', 'lib')
                if os.path.exists(lib_path):
                    options.library_search_paths.append(lib_path)
            # For version-based dependencies, check standard locations
            else:
                # Check common installation paths
                standard_paths = [
                    os.path.expanduser(f'~/.nlpl/lib/{dep_name}'),
                    f'/usr/local/lib/nlpl/{dep_name}',
                    f'/usr/lib/nlpl/{dep_name}'
                ]
                for path in standard_paths:
                    if os.path.exists(path):
                        options.library_search_paths.append(path)
                        break
        
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
        
        # Detect main entry point and module structure
        main_file = self._detect_main_entry_point(sources)
        module_files = self._group_into_modules(sources)
        
        success_count = 0
        compiled_objects = []  # For linking multi-file modules
        
        # Handle multi-file modules properly
        # Strategy: Compile each file to intermediate format, then link if needed
        for source_path in sources:
            # Determine output path
            rel_path = os.path.relpath(source_path, src_dir)
            base_name = os.path.splitext(rel_path)[0]
            
            # Determine if this is the main file
            is_main = (source_path == main_file)
            
            # For C/C++ targets with multiple files, compile to object files first
            if self.config.build.target in [CompilationTarget.C, CompilationTarget.CPP]:
                if len(sources) > 1:
                    # Multi-file project: compile to intermediate C/C++ first
                    intermediate_file = os.path.join(out_dir, f"{base_name}.{self.config.build.target}")
                    output_file = intermediate_file
                else:
                    # Single file: compile and link directly to executable
                    output_file = os.path.join(out_dir, base_name if is_main else base_name)
            else:
                # For other targets, use appropriate extension
                output_file = os.path.join(out_dir, base_name)
                if self.config.build.target not in ["c", "cpp", "asm"]:
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
                
                # Compile to intermediate format
                if self.config.build.target in [CompilationTarget.C, CompilationTarget.CPP]:
                    # For multi-file projects, compile to C/C++ source
                    ok, libs = self.compiler.compile(ast, self.config.build.target, output_file)
                    if ok:
                        compiled_objects.append(output_file)
                        success_count += 1
                    else:
                        return False
                else:
                    # For other targets, compile directly
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
        
        # Link multi-file C/C++ projects
        if self.config.build.target in [CompilationTarget.C, CompilationTarget.CPP] and len(compiled_objects) > 1:
            print(f"\n  Linking {len(compiled_objects)} object files...")
            final_executable = os.path.join(out_dir, self.config.package.name)
            if not self._link_multi_file_project(compiled_objects, final_executable):
                return False
                
        print(f"✓ Built {success_count} files to {out_dir}")
        return True

    def run(self):
        """Run the built executable."""
        out_dir = self.config.build.output_dir
        
        # Better main entry point detection using multiple strategies
        executable = self._find_executable(out_dir)
        
        if executable:
            print(f"Running {executable}...")
            import subprocess
            try:
                result = subprocess.run([executable], cwd=out_dir)
                return result.returncode == 0
            except Exception as e:
                print(f"✗ Failed to run executable: {e}")
                return False
        else:
            print("✗ No executable found to run")
            print(f"   Searched in: {out_dir}")
            return False
    
    def _detect_main_entry_point(self, sources: List[str]) -> Optional[str]:
        """Detect the main entry point file from a list of sources.
        
        Strategies:
        1. Look for file named 'main.nlpl'
        2. Look for file with same name as package
        3. Look for file containing a main() function
        4. Default to first file if none found
        """
        # Strategy 1: main.nlpl
        for source in sources:
            if os.path.basename(source).lower() == 'main.nlpl':
                return source
        
        # Strategy 2: package name
        package_file = f"{self.config.package.name}.nlpl"
        for source in sources:
            if os.path.basename(source).lower() == package_file.lower():
                return source
        
        # Strategy 3: File containing main() function
        for source in sources:
            try:
                with open(source, 'r') as f:
                    content = f.read()
                    # Simple heuristic: look for 'function main' or 'define a function called main'
                    if 'function main' in content.lower() or 'called main' in content.lower():
                        return source
            except:
                continue
        
        # Strategy 4: Default to first file
        return sources[0] if sources else None
    
    def _group_into_modules(self, sources: List[str]) -> Dict[str, List[str]]:
        """Group source files into modules based on directory structure.
        
        Returns:
            Dictionary mapping module names to list of source files
        """
        modules = {}
        src_dir = self.config.build.source_dir
        
        for source in sources:
            rel_path = os.path.relpath(source, src_dir)
            dir_name = os.path.dirname(rel_path)
            
            # If file is in a subdirectory, that's the module name
            if dir_name:
                module_name = dir_name.replace(os.sep, '.')
            else:
                module_name = 'main'
            
            if module_name not in modules:
                modules[module_name] = []
            modules[module_name].append(source)
        
        return modules
    
    def _link_multi_file_project(self, object_files: List[str], output_executable: str) -> bool:
        """Link multiple C/C++ source files into a single executable.
        
        Args:
            object_files: List of compiled C/C++ source files
            output_executable: Path to output executable
            
        Returns:
            True if linking succeeded, False otherwise
        """
        import subprocess
        import shutil
        
        # Choose compiler based on target
        if self.config.build.target == CompilationTarget.CPP:
            compilers = ['g++', 'clang++']
        else:
            compilers = ['gcc', 'clang']
        
        compiler = None
        for c in compilers:
            if shutil.which(c):
                compiler = c
                break
        
        if not compiler:
            print(f"✗ No C/C++ compiler found for linking")
            return False
        
        # Build linker command
        cmd = [compiler] + object_files + ['-o', output_executable]
        
        # Add library search paths
        for path in self.compiler.options.library_search_paths:
            cmd.append(f'-L{path}')
        
        # Add optimization flags
        if self.compiler.options.optimization_level > 0:
            cmd.append(f'-O{self.compiler.options.optimization_level}')
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Linking successful: {output_executable}")
                return True
            else:
                print(f"✗ Linking failed:")
                print(result.stderr)
                return False
        except Exception as e:
            print(f"✗ Linking error: {e}")
            return False
    
    def _find_executable(self, out_dir: str) -> Optional[str]:
        """Find the executable in the output directory using multiple strategies.
        
        Strategies:
        1. Look for file matching package name (no extension)
        2. Look for 'main' executable
        3. Look for any executable file (has execute permission)
        4. Look for newest file without source extension
        
        Returns:
            Path to executable if found, None otherwise
        """
        # Strategy 1: Package name
        executable = os.path.join(out_dir, self.config.package.name)
        if os.path.exists(executable) and os.access(executable, os.X_OK):
            return executable
        
        # Strategy 2: 'main'
        executable = os.path.join(out_dir, 'main')
        if os.path.exists(executable) and os.access(executable, os.X_OK):
            return executable
        
        # Strategy 3: Any executable file
        files = glob.glob(os.path.join(out_dir, '*'))
        for f in files:
            # Skip directories, object files, and source files
            if (os.path.isfile(f) and 
                os.access(f, os.X_OK) and 
                not f.endswith(('.o', '.c', '.cpp', '.h', '.nlpl', '.ll', '.js', '.ts'))):
                return f
        
        # Strategy 4: Newest file without source extension
        candidates = []
        for f in files:
            if (os.path.isfile(f) and 
                not f.endswith(('.o', '.c', '.cpp', '.h', '.nlpl', '.ll', '.js', '.ts'))):
                candidates.append((os.path.getmtime(f), f))
        
        if candidates:
            candidates.sort(reverse=True)  # Newest first
            return candidates[0][1]
        
        return None
