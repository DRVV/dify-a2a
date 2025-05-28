#!/usr/bin/env python3
"""
Enhanced test runner for Dify Orchestrator with pytest.
This script provides a convenient interface for running different types of tests.
"""

import sys
import subprocess
import argparse
import os


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Error: pytest not found. Please install test dependencies:")
        print("   pip install -e .[test]")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Enhanced test runner for Dify Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                     # Run all tests
  python run_tests.py --unit              # Run only unit tests
  python run_tests.py --integration       # Run only integration tests
  python run_tests.py --coverage          # Run with coverage report
  python run_tests.py --performance       # Run performance tests
  python run_tests.py --parallel          # Run tests in parallel
  python run_tests.py --html              # Generate HTML report
  python run_tests.py --backwards         # Run backward compatibility tests
  python run_tests.py --quick             # Quick test run (unit tests only)
        """
    )
    
    # Test type options
    parser.add_argument(
        '--unit', action='store_true',
        help='Run only unit tests (fast, mocked dependencies)'
    )
    parser.add_argument(
        '--integration', action='store_true',
        help='Run only integration tests (requires environment setup)'
    )
    parser.add_argument(
        '--performance', action='store_true',
        help='Run performance and stress tests'
    )
    parser.add_argument(
        '--backwards', action='store_true',
        help='Run backward compatibility tests'
    )
    parser.add_argument(
        '--slow', action='store_true',
        help='Include slow tests'
    )
    
    # Output and reporting options
    parser.add_argument(
        '--coverage', action='store_true',
        help='Generate coverage report'
    )
    parser.add_argument(
        '--html', action='store_true',
        help='Generate HTML test report'
    )
    parser.add_argument(
        '--parallel', action='store_true',
        help='Run tests in parallel'
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--quiet', '-q', action='store_true',
        help='Quiet output'
    )
    
    # Convenience options
    parser.add_argument(
        '--quick', action='store_true',
        help='Quick test run (unit tests only, no coverage)'
    )
    parser.add_argument(
        '--all', action='store_true',
        help='Run all tests including slow ones'
    )
    parser.add_argument(
        '--install-deps', action='store_true',
        help='Install test dependencies before running tests'
    )
    
    # Pytest pass-through options
    parser.add_argument(
        '--pytest-args', 
        help='Additional arguments to pass to pytest'
    )
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not os.path.exists('orchestrator.py'):
        print("❌ Error: orchestrator.py not found. Please run this script from the dify_orch directory.")
        return 1
    
    # Install dependencies if requested
    if args.install_deps:
        print("Installing test dependencies...")
        # Try uv first, fallback to pip
        if os.path.exists('.venv') and not os.path.exists('.venv/bin/pip'):
            install_cmd = ['uv', 'add', 'pytest', 'pytest-cov', 'pytest-mock']
        else:
            install_cmd = [sys.executable, '-m', 'pip', 'install', '-e', '.[test]']
        if not run_command(install_cmd, "Installing test dependencies"):
            return 1
    
    # Build the pytest command - use local venv if available
    python_cmd = '.venv/bin/python' if os.path.exists('.venv/bin/python') else sys.executable
    cmd = [python_cmd, '-m', 'pytest']
    
    # Handle quick mode
    if args.quick:
        cmd.extend(['-m', 'unit', '--tb=short', '-q'])
        description = "Quick unit tests"
    else:
        # Add markers based on test type selection
        markers = []
        
        if args.unit:
            markers.append('unit')
        if args.integration:
            markers.append('integration')
        if args.performance:
            markers.append('performance')
        if args.backwards:
            markers.append('backward_compatibility')
        
        if markers:
            cmd.extend(['-m', ' or '.join(markers)])
        
        # Handle slow tests
        if not args.slow and not args.all and not args.performance:
            cmd.extend(['-m', 'not slow'])
        
        # Add coverage if requested
        if args.coverage or args.all:
            cmd.extend(['--cov=orchestrator', '--cov-report=term-missing'])
            if args.html:
                cmd.append('--cov-report=html')
        
        # Add HTML report if requested
        if args.html:
            cmd.extend(['--html=test_report.html', '--self-contained-html'])
        
        # Add parallel execution if requested
        if args.parallel:
            cmd.extend(['-n', 'auto'])
        
        # Handle verbosity
        if args.verbose:
            cmd.append('-v')
        elif args.quiet:
            cmd.append('-q')
        
        description = "Pytest test suite"
    
    # Add any additional pytest arguments
    if args.pytest_args:
        cmd.extend(args.pytest_args.split())
    
    # Add tests directory
    cmd.append('tests/')
    
    # Run the tests
    success = run_command(cmd, description)
    
    if success:
        print(f"\n🎉 Tests completed successfully!")
        
        if args.coverage or args.all:
            print("\n📊 Coverage report generated:")
            print("   - Terminal: See above")
            if args.html:
                print("   - HTML: htmlcov/index.html")
        
        if args.html:
            print(f"\n📄 HTML test report: test_report.html")
        
        print(f"\n💡 Tips:")
        print(f"   - Run 'python run_tests.py --quick' for fast feedback")
        print(f"   - Run 'python run_tests.py --integration' to test with real APIs")
        print(f"   - Run 'python run_tests.py --all' for comprehensive testing")
        
    else:
        print(f"\n❌ Tests failed. Check the output above for details.")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
