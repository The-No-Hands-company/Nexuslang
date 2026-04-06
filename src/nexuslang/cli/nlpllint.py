#!/usr/bin/env python3
"""
nlpllint - NexusLang Static Analyzer
================================

Command-line interface for NexusLang static analysis.

Usage:
    nlpllint file.nlpl                  # Analyze single file
    nlpllint dir/                       # Analyze directory
    nlpllint --strict file.nlpl         # Strict mode (all checks)
    nlpllint --json file.nlpl           # JSON output
    nlpllint --fix file.nlpl            # Auto-fix issues
    nlpllint --help                     # Show help
"""

import sys
import os
import argparse
import json
from pathlib import Path
from typing import List, Optional

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from nexuslang.tooling.analyzer import StaticAnalyzer, AnalysisReport
from nexuslang.tooling.analyzer.analyzer import (
    create_default_analyzer,
    create_strict_analyzer,
    create_minimal_analyzer
)
from nexuslang.tooling.analyzer.report import Severity
from nexuslang.tooling.analyzer.autofix import AutoFixer
from nexuslang.tooling.analyzer.ide_hooks import IDEHooks, LspFormatter


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='NLPL Static Analyzer - Catch bugs before runtime',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'path',
        help='File or directory to analyze'
    )
    
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Recursively analyze directory (default: True)'
    )
    
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Strict mode (enable all checks including style)'
    )
    
    parser.add_argument(
        '--minimal',
        action='store_true',
        help='Minimal mode (only critical checks: memory, null, init)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format'
    )
    
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Automatically fix issues where possible'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what --fix would change without writing files'
    )

    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    
    parser.add_argument(
        '--errors-only',
        action='store_true',
        help='Show only errors (suppress warnings and info)'
    )
    
    parser.add_argument(
        '--max-issues',
        type=int,
        default=None,
        help='Maximum number of issues to display'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file (TODO)'
    )
    
    args = parser.parse_args()
    
    # Check path exists
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path not found: {args.path}", file=sys.stderr)
        return 1
    
    # Create analyzer
    if args.strict:
        analyzer = create_strict_analyzer()
    elif args.minimal:
        analyzer = create_minimal_analyzer()
    else:
        analyzer = create_default_analyzer()
    
    # Analyze
    try:
        if path.is_file():
            reports = [analyzer.analyze_file(str(path))]
        else:
            reports = analyzer.analyze_directory(str(path), recursive=args.recursive)
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        return 1
    
    # Auto-fix pass (runs before output so the summary reflects remaining issues)
    if args.fix or getattr(args, 'dry_run', False):
        dry_run = getattr(args, 'dry_run', False)
        _apply_fixes(reports, dry_run=dry_run, use_colors=not getattr(args, 'no_color', False))

    # Output results
    use_colors = not args.no_color and sys.stdout.isatty()
    
    if args.json:
        output_json(reports)
    else:
        return output_text(reports, use_colors, args.errors_only, args.max_issues)


def _apply_fixes(
    reports: List[AnalysisReport],
    dry_run: bool = False,
    use_colors: bool = True,
) -> None:
    """
    Run the AutoFixer over every report and print a summary.
    In dry-run mode the modified source is printed instead of written.
    """
    fixer = AutoFixer()
    bold = '\033[1m' if use_colors else ''
    green = '\033[92m' if use_colors else ''
    yellow = '\033[93m' if use_colors else ''
    reset = '\033[0m' if use_colors else ''

    mode_label = "[dry-run] " if dry_run else ""
    total_applied = 0
    total_skipped = 0

    for report in reports:
        if not report.issues:
            continue
        try:
            result = fixer.apply_to_file(
                report.file_path, report.issues, dry_run=dry_run
            )
        except (OSError, IOError) as exc:
            print(f"{yellow}Warning: could not fix {report.file_path}: {exc}{reset}")
            continue

        if result.applied:
            print(f"{bold}{mode_label}Fixed {result.applied} issue(s) in "
                  f"{report.file_path}{reset}")
            for change in result.changes:
                print(f"  {green}+ {change}{reset}")
            if dry_run:
                print(f"  {yellow}(dry-run: file not written){reset}")
        total_applied += result.applied
        total_skipped += result.skipped

    if total_applied or total_skipped:
        print(f"\n{bold}Fix summary:{reset} applied={total_applied} "
              f"no-structured-fix={total_skipped}\n")


def output_text(reports: List[AnalysisReport], 
                use_colors: bool,
                errors_only: bool,
                max_issues: Optional[int]) -> int:
    """Output results in text format."""
    total_errors = 0
    total_warnings = 0
    total_issues = 0
    
    for report in reports:
        # Filter if errors only
        if errors_only:
            issues = report.filter(severity=Severity.ERROR)
        else:
            issues = report.issues
        
        # Skip files with no issues
        if not issues:
            continue
        
        # Print summary
        print(report.summary(use_colors))
        
        # Print issues
        if issues:
            print(report.format_all(
                show_source=True,
                use_colors=use_colors,
                max_issues=max_issues
            ))
            print()
        
        # Count
        counts = report.count_by_severity()
        total_errors += counts[Severity.ERROR]
        total_warnings += counts[Severity.WARNING]
        total_issues += len(issues)
    
    # Overall summary
    if len(reports) > 1:
        if use_colors:
            red = '\033[91m'
            yellow = '\033[93m'
            bold = '\033[1m'
            reset = '\033[0m'
        else:
            red = yellow = bold = reset = ''
        
        print(f"\n{bold}Overall Summary{reset}")
        print(f"{'=' * 60}")
        print(f"  Files analyzed: {len(reports)}")
        print(f"  {red}Total errors:   {total_errors}{reset}")
        print(f"  {yellow}Total warnings: {total_warnings}{reset}")
        print(f"  Total issues:   {total_issues}")
        print(f"{'=' * 60}\n")
    
    # Return exit code
    return 1 if total_errors > 0 else 0


def output_json(reports: List[AnalysisReport]):
    """Output results in JSON format."""
    output = {
        'files': [],
        'summary': {
            'total_files': len(reports),
            'total_errors': 0,
            'total_warnings': 0,
            'total_info': 0,
            'total_hints': 0,
        }
    }
    
    for report in reports:
        counts = report.count_by_severity()
        
        file_data = {
            'path': report.file_path,
            'lines_analyzed': report.lines_analyzed,
            'total_lines': report.total_lines,
            'analysis_time_ms': report.analysis_time_ms,
            'issues': [],
            'counts': {
                'errors': counts[Severity.ERROR],
                'warnings': counts[Severity.WARNING],
                'info': counts[Severity.INFO],
                'hints': counts[Severity.HINT],
            }
        }
        
        for issue in report.issues:
            issue_data = {
                'code': issue.code,
                'severity': issue.severity.value,
                'category': issue.category.value,
                'message': issue.message,
                'location': {
                    'file': issue.location.file,
                    'line': issue.location.line,
                    'column': issue.location.column,
                },
            }
            
            if issue.suggestion:
                issue_data['suggestion'] = issue.suggestion
            if issue.fix:
                issue_data['fix'] = issue.fix
            if issue.help_url:
                issue_data['help_url'] = issue.help_url
            
            file_data['issues'].append(issue_data)
        
        output['files'].append(file_data)
        
        # Update summary
        output['summary']['total_errors'] += counts[Severity.ERROR]
        output['summary']['total_warnings'] += counts[Severity.WARNING]
        output['summary']['total_info'] += counts[Severity.INFO]
        output['summary']['total_hints'] += counts[Severity.HINT]
    
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    sys.exit(main())
