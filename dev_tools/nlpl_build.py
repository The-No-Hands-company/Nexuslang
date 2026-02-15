#!/usr/bin/env python3
"""
NLPL Build Tool - Project-aware build system

Provides Cargo-like build commands for NLPL projects with nlpl.toml manifests.
Integrates with the existing nlplc compiler and provides build orchestration,
dependency management, and feature flag support.

Usage:
    nlpl_build.py build                    # Build all targets
    nlpl_build.py build --release          # Build with release profile
    nlpl_build.py build --features csv,db  # Build with specific features
    nlpl_build.py clean                    # Clean build artifacts
    nlpl_build.py test                     # Run tests
    nlpl_build.py run                      # Run default binary
    nlpl_build.py run --bin analyzer       # Run specific binary
    nlpl_build.py check                    # Check project without building
"""

import sys
import os
import argparse
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional, Set, Dict
from dataclasses import dataclass

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nlpl.build.manifest import load_manifest, Manifest, BuildProfile, BinaryTarget
from nlpl.parser.lexer import Lexer
from nlpl.parser.parser import Parser
from nlpl.compiler import Compiler, CompilerOptions


@dataclass
class BuildContext:
    """Build context with manifest and configuration."""
    manifest: Manifest
    profile: BuildProfile
    features: Set[str]
    verbose: bool
    build_dir: Path
    
    def __post_init__(self):
        """Ensure build directory exists."""
        self.build_dir.mkdir(parents=True, exist_ok=True)


class BuildTool:
    """NLPL Build Tool - manages compilation of NLPL projects."""
    
    def __init__(self, manifest_path: Optional[str] = None, verbose: bool = False):
        """
        Initialize build tool.
        
        Args:
            manifest_path: Path to nlpl.toml. If None, searches current directory.
            verbose: Enable verbose output
        """
        self.manifest = load_manifest(manifest_path)
        self.verbose = verbose
        self.project_root = self.manifest.project_root
        
        # Default build directory
        self.build_dir = self.project_root / 'build'
        
        if self.verbose:
            print(f"Project: {self.manifest.package.name if self.manifest.package else 'workspace'}")
            print(f"Root: {self.project_root}")
    
    def build(
        self,
        profile_name: str = 'dev',
        features: Optional[List[str]] = None,
        bins: Optional[List[str]] = None
    ) -> bool:
        """
        Build project with specified profile and features.
        
        Args:
            profile_name: Build profile ('dev', 'release', or custom)
            features: List of feature flags to enable
            bins: Specific binaries to build (None = all)
        
        Returns:
            True if build succeeded, False otherwise
        """
        # Get build profile
        try:
            profile = self.manifest.get_profile(profile_name)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return False
        
        # Resolve features
        enabled_features = self._resolve_features(features or [])
        
        # Create build context
        ctx = BuildContext(
            manifest=self.manifest,
            profile=profile,
            features=enabled_features,
            verbose=self.verbose,
            build_dir=self.build_dir / profile_name
        )
        
        print(f"Building {self.manifest.package.name if self.manifest.package else 'project'} " +
              f"[profile: {profile_name}, features: {','.join(enabled_features) if enabled_features else 'none'}]")
        
        # Build targets
        success = True
        
        # Build library target if exists
        if self.manifest.library_target:
            print(f"  Compiling library {self.manifest.library_target.name}...")
            if not self._build_library(ctx):
                success = False
        
        # Build binary targets
        binary_targets = self.manifest.binary_targets
        if bins:
            # Filter to requested binaries
            binary_targets = [t for t in binary_targets if t.name in bins]
            if len(binary_targets) != len(bins):
                found = {t.name for t in binary_targets}
                missing = set(bins) - found
                print(f"Error: Unknown binaries: {', '.join(missing)}", file=sys.stderr)
                return False
        
        for target in binary_targets:
            # Check if target requires features we don't have
            if target.required_features:
                missing = set(target.required_features) - enabled_features
                if missing:
                    if self.verbose:
                        print(f"  Skipping {target.name} (missing features: {', '.join(missing)})")
                    continue
            
            print(f"  Compiling binary {target.name}...")
            if not self._build_binary(ctx, target):
                success = False
        
        if success:
            print(f"Finished build [profile: {profile_name}]")
        else:
            print("Build failed", file=sys.stderr)
        
        return success
    
    def clean(self) -> bool:
        """
        Remove build artifacts.
        
        Returns:
            True if clean succeeded
        """
        print("Cleaning build artifacts...")
        
        if self.build_dir.exists():
            try:
                shutil.rmtree(self.build_dir)
                if self.verbose:
                    print(f"Removed {self.build_dir}")
            except Exception as e:
                print(f"Error cleaning build directory: {e}", file=sys.stderr)
                return False
        
        # Clean any .o, .ll, .bc files in project root
        for pattern in ['*.o', '*.ll', '*.bc']:
            for file in self.project_root.glob(pattern):
                try:
                    file.unlink()
                    if self.verbose:
                        print(f"Removed {file}")
                except Exception as e:
                    print(f"Error removing {file}: {e}", file=sys.stderr)
        
        print("Cleaned successfully")
        return True
    
    def check(self, features: Optional[List[str]] = None) -> bool:
        """
        Check project for errors without building.
        
        Args:
            features: List of feature flags to enable
        
        Returns:
            True if check passed, False otherwise
        """
        print("Checking project...")
        
        enabled_features = self._resolve_features(features or [])
        
        # Check all source files
        success = True
        
        # Check library
        if self.manifest.library_target:
            lib_path = self.manifest.resolve_path(self.manifest.library_target.path)
            print(f"  Checking {self.manifest.library_target.name}...")
            if not self._check_file(lib_path):
                success = False
        
        # Check binaries
        for target in self.manifest.binary_targets:
            # Check features
            if target.required_features:
                missing = set(target.required_features) - enabled_features
                if missing:
                    if self.verbose:
                        print(f"  Skipping {target.name} (missing features: {', '.join(missing)})")
                    continue
            
            bin_path = self.manifest.resolve_path(target.path)
            print(f"  Checking {target.name}...")
            if not self._check_file(bin_path):
                success = False
        
        if success:
            print("Check completed successfully")
        else:
            print("Check found errors", file=sys.stderr)
        
        return success
    
    def run(
        self,
        bin_name: Optional[str] = None,
        profile_name: str = 'dev',
        features: Optional[List[str]] = None,
        args: Optional[List[str]] = None
    ) -> bool:
        """
        Build and run a binary target.
        
        Args:
            bin_name: Binary to run (None = default/first)
            profile_name: Build profile
            features: Feature flags
            args: Arguments to pass to binary
        
        Returns:
            True if successful
        """
        # Determine which binary to run
        if not self.manifest.binary_targets:
            print("Error: No binary targets defined", file=sys.stderr)
            return False
        
        if bin_name:
            target = next((t for t in self.manifest.binary_targets if t.name == bin_name), None)
            if not target:
                print(f"Error: Binary '{bin_name}' not found", file=sys.stderr)
                return False
        else:
            # Use first binary
            target = self.manifest.binary_targets[0]
        
        # Build first
        if not self.build(profile_name=profile_name, features=features, bins=[target.name]):
            print("Build failed, cannot run", file=sys.stderr)
            return False
        
        # Run the binary
        binary_path = self.build_dir / profile_name / target.name
        if not binary_path.exists():
            print(f"Error: Binary not found at {binary_path}", file=sys.stderr)
            return False
        
        print(f"Running {target.name}...")
        try:
            result = subprocess.run(
                [str(binary_path)] + (args or []),
                cwd=self.project_root
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Error running binary: {e}", file=sys.stderr)
            return False
    
    def test(self, profile_name: str = 'dev', features: Optional[List[str]] = None) -> bool:
        """
        Run project tests.
        
        Args:
            profile_name: Build profile
            features: Feature flags
        
        Returns:
            True if all tests passed
        """
        print("Running tests...")
        
        # Build with test profile
        if not self.build(profile_name=profile_name, features=features):
            print("Build failed, cannot run tests", file=sys.stderr)
            return False
        
        # Look for test binaries (convention: files in tests/ directory)
        test_dir = self.project_root / 'tests'
        if not test_dir.exists():
            print("No tests directory found")
            return True
        
        # Run all test binaries
        test_files = list(test_dir.glob('**/*.nlpl'))
        if not test_files:
            print("No test files found")
            return True
        
        print(f"Running {len(test_files)} test(s)...")
        
        passed = 0
        failed = 0
        
        for test_file in test_files:
            test_name = test_file.stem
            print(f"  Testing {test_name}...", end=" ")
            
            # Compile and run test
            output = self.build_dir / profile_name / f"test_{test_name}"
            if self._compile_single_file(test_file, output, profile_name):
                try:
                    result = subprocess.run(
                        [str(output)],
                        capture_output=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        print("ok")
                        passed += 1
                    else:
                        print("FAILED")
                        if self.verbose and result.stderr:
                            print(f"    {result.stderr.decode()}")
                        failed += 1
                except subprocess.TimeoutExpired:
                    print("TIMEOUT")
                    failed += 1
                except Exception as e:
                    print(f"ERROR: {e}")
                    failed += 1
            else:
                print("COMPILE FAILED")
                failed += 1
        
        print(f"\nTest result: {passed} passed, {failed} failed")
        return failed == 0
    
    def _resolve_features(self, requested: List[str]) -> Set[str]:
        """
        Resolve feature flags and their dependencies.
        
        Args:
            requested: List of requested feature names
        
        Returns:
            Set of all enabled features (including transitive dependencies)
        """
        enabled = set()
        to_process = list(requested)
        
        while to_process:
            feature = to_process.pop()
            if feature in enabled:
                continue
            
            if not self.manifest.has_feature(feature):
                print(f"Warning: Unknown feature '{feature}'", file=sys.stderr)
                continue
            
            enabled.add(feature)
            
            # Add feature dependencies
            deps = self.manifest.get_feature_dependencies(feature)
            to_process.extend(deps)
        
        return enabled
    
    def _build_library(self, ctx: BuildContext) -> bool:
        """Build library target."""
        lib_path = self.manifest.resolve_path(self.manifest.library_target.path)
        output = ctx.build_dir / f"lib{self.manifest.library_target.name}.a"
        
        return self._compile_single_file(lib_path, output, ctx.profile.name)
    
    def _build_binary(self, ctx: BuildContext, target: BinaryTarget) -> bool:
        """Build binary target."""
        bin_path = self.manifest.resolve_path(target.path)
        output = ctx.build_dir / target.name
        
        return self._compile_single_file(bin_path, output, ctx.profile.name)
    
    def _compile_single_file(self, source: Path, output: Path, profile: str) -> bool:
        """
        Compile single NLPL file to executable.
        
        Args:
            source: Source file path
            output: Output binary path
            profile: Build profile name
        
        Returns:
            True if compilation succeeded
        """
        if not source.exists():
            print(f"Error: Source file not found: {source}", file=sys.stderr)
            return False
        
        try:
            # Read source
            with open(source, 'r') as f:
                source_code = f.read()
            
            # Parse
            lexer = Lexer(source_code)
            tokens = lexer.scan_tokens()
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Get profile for compiler options
            build_profile = self.manifest.get_profile(profile)
            
            # Set up compiler options
            options = CompilerOptions()
            options.optimization_level = build_profile.opt_level
            options.debug_info = build_profile.debug
            
            # Compile
            compiler = Compiler(options)
            
            # Use nlplc to compile (shell out for now)
            # TODO: Use compiler API directly when stable
            nlplc = self.project_root.parent / "dev_tools" / "nlplc"
            if not nlplc.exists():
                nlplc = Path(__file__).parent / "nlplc"
            
            cmd = [
                str(nlplc),
                str(source),
                "-o", str(output)
            ]
            
            if build_profile.opt_level > 0:
                cmd.extend(["-O", str(build_profile.opt_level)])
            
            if build_profile.debug:
                cmd.append("--debug")
            
            if self.verbose:
                cmd.append("--verbose")
            
            result = subprocess.run(cmd, capture_output=not self.verbose)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error compiling {source.name}: {e}", file=sys.stderr)
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def _check_file(self, source: Path) -> bool:
        """
        Check source file for errors without compiling.
        
        Args:
            source: Source file path
        
        Returns:
            True if no errors found
        """
        if not source.exists():
            print(f"Error: Source file not found: {source}", file=sys.stderr)
            return False
        
        try:
            with open(source, 'r') as f:
                source_code = f.read()
            
            lexer = Lexer(source_code)
            tokens = lexer.scan_tokens()
            parser = Parser(tokens)
            parser.parse()
            
            return True
            
        except Exception as e:
            print(f"Error in {source.name}: {e}", file=sys.stderr)
            return False


def main():
    """Main entry point for nlpl_build CLI."""
    parser = argparse.ArgumentParser(
        description="NLPL Build Tool - Project-aware build system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Global options
    parser.add_argument("--manifest-path", help="Path to nlpl.toml (default: search current directory)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Build command")
    
    # build command
    build_parser = subparsers.add_parser("build", help="Build project")
    build_parser.add_argument("--release", action="store_true", help="Build with release profile")
    build_parser.add_argument("--profile", help="Build with custom profile")
    build_parser.add_argument("--features", help="Comma-separated list of features to enable")
    build_parser.add_argument("--bin", action="append", dest="bins", help="Build specific binary (can be used multiple times)")
    
    # clean command
    clean_parser = subparsers.add_parser("clean", help="Remove build artifacts")
    
    # check command
    check_parser = subparsers.add_parser("check", help="Check project for errors")
    check_parser.add_argument("--features", help="Comma-separated list of features to enable")
    
    # run command
    run_parser = subparsers.add_parser("run", help="Build and run binary")
    run_parser.add_argument("--bin", dest="bin_name", help="Binary to run (default: first)")
    run_parser.add_argument("--release", action="store_true", help="Run with release profile")
    run_parser.add_argument("--profile", help="Run with custom profile")
    run_parser.add_argument("--features", help="Comma-separated list of features to enable")
    run_parser.add_argument("args", nargs="*", help="Arguments to pass to binary")
    
    # test command
    test_parser = subparsers.add_parser("test", help="Run project tests")
    test_parser.add_argument("--release", action="store_true", help="Test with release profile")
    test_parser.add_argument("--profile", help="Test with custom profile")
    test_parser.add_argument("--features", help="Comma-separated list of features to enable")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Create build tool
    try:
        tool = BuildTool(manifest_path=args.manifest_path, verbose=args.verbose)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Run this command from a directory containing nlpl.toml", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error loading manifest: {e}", file=sys.stderr)
        return 1
    
    # Execute command
    try:
        if args.command == "build":
            profile = "release" if args.release else (args.profile or "dev")
            features = args.features.split(",") if args.features else None
            success = tool.build(profile_name=profile, features=features, bins=args.bins)
            
        elif args.command == "clean":
            success = tool.clean()
            
        elif args.command == "check":
            features = args.features.split(",") if args.features else None
            success = tool.check(features=features)
            
        elif args.command == "run":
            profile = "release" if args.release else (args.profile or "dev")
            features = args.features.split(",") if args.features else None
            success = tool.run(
                bin_name=args.bin_name,
                profile_name=profile,
                features=features,
                args=args.args
            )
            
        elif args.command == "test":
            profile = "release" if args.release else (args.profile or "dev")
            features = args.features.split(",") if args.features else None
            success = tool.test(profile_name=profile, features=features)
            
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
