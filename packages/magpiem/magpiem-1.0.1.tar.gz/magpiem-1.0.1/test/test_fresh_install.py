#!/usr/bin/env python3
"""
Test that package installs correctly in a fresh environment
and all dependencies are properly specified.
"""

import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """Run a command and return result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False
    )
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed with return code {result.returncode}")
    
    return result


def test_fresh_install():
    """Test installation in a fresh virtual environment."""
    project_root = Path(__file__).parent.parent
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"\nCreating temporary test environment in: {temp_dir}")
        
        venv_path = Path(temp_dir) / "test_venv"
        
        print("\n1. Creating virtual environment...")
        python_exe = sys.executable
        run_command([python_exe, "-m", "venv", str(venv_path)])
        
        if sys.platform == "win32":
            venv_python = venv_path / "Scripts" / "python.exe"
            venv_pip = venv_path / "Scripts" / "pip.exe"
        else:
            venv_python = venv_path / "bin" / "python"
            venv_pip = venv_path / "bin" / "pip"
        
        print("\n2. Upgrading pip...")
        run_command([str(venv_pip), "install", "--upgrade", "pip"])
        
        print("\n3. Building package...")
        run_command([str(venv_python), "-m", "pip", "install", "build"])
        run_command([str(venv_python), "-m", "build"], cwd=str(project_root))
        
        print("\n4. Installing built package...")
        dist_dir = project_root / "dist"
        wheel_files = list(dist_dir.glob("*.whl"))
        if not wheel_files:
            raise RuntimeError("No wheel file found in dist/")
        
        latest_wheel = max(wheel_files, key=os.path.getmtime)
        print(f"Installing: {latest_wheel.name}")
        run_command([str(venv_pip), "install", str(latest_wheel)])
        
        print("\n5. Testing imports...")
        test_imports = [
            "import magpiem",
            "from magpiem import processing_cpp",
            "from magpiem.dash import dash_ui",
            "from magpiem.io import io_utils",
            "from magpiem.plotting import plotting_utils",
            "from magpiem.processing import processing_utils",
            "from magpiem.processing.classes import Tomogram, Particle, Cleaner",
            "print('All imports successful!')"
        ]
        
        import_script = "; ".join(test_imports)
        result = run_command(
            [str(venv_python), "-c", import_script],
            check=False
        )
        
        if result.returncode != 0:
            print("\nFAILED: Import test failed")
            print("This likely indicates missing dependencies in pyproject.toml")
            return False
        
        print("\nAll imports successful!")
        
        print("\n6. Verifying dependencies...")
        result = run_command(
            [str(venv_pip), "check"],
            check=False
        )
        
        if result.returncode != 0:
            print("\nFAILED: Dependency check failed")
            return False
        
        print("\nAll dependencies satisfied!")
        
        print("\n7. Testing entry point...")
        result = run_command(
            [str(venv_python), "-c", 
             "import sys; from magpiem.dash.dash_ui import main; "
             "print('Entry point import successful')"],
            check=False
        )
        
        if result.returncode != 0:
            print("\nFAILED: Entry point test failed")
            return False
        
        print("\nEntry point accessible!")
        
    print("\n" + "="*60)
    print("All fresh install tests passed!")
    print("="*60)
    return True


if __name__ == "__main__":
    try:
        success = test_fresh_install()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nTest failed with exception: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

