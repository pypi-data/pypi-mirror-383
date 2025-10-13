#!/usr/bin/env python3
"""
Diagnostic script to check catpic installation and test prerequisites.
Run this before running pytest to identify issues.

Usage:
    cd python
    uv run python test_diagnostics.py
"""

import sys
import traceback
from pathlib import Path

def check_imports():
    """Check if all catpic modules can be imported."""
    print("=" * 60)
    print("CHECKING IMPORTS")
    print("=" * 60)
    
    modules = [
        'catpic',
        'catpic.core',
        'catpic.encoder',
        'catpic.decoder',
        'catpic.primitives',
        'catpic.cli',
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except Exception as e:
            print(f"✗ {module}: {e}")
            traceback.print_exc()
            all_ok = False
    
    return all_ok

def check_exports():
    """Check if expected functions/classes are exported."""
    print("\n" + "=" * 60)
    print("CHECKING EXPORTS")
    print("=" * 60)
    
    try:
        import catpic
        
        # High-level API
        high_level = ['render_image_ansi', 'load_meow', 'save_meow']
        
        # Primitives API
        primitives = [
            'Cell',
            'get_full_glut',
            'get_pips_glut',
            'quantize_cell',
            'compute_centroid',
            'pattern_to_index',
            'process_cell',
            'image_to_cells',
            'cells_to_ansi_lines',
        ]
        
        all_ok = True
        
        print("\nHigh-level API:")
        for name in high_level:
            if hasattr(catpic, name):
                print(f"  ✓ {name}")
            else:
                print(f"  ✗ {name} - NOT FOUND")
                all_ok = False
        
        print("\nPrimitives API:")
        for name in primitives:
            if hasattr(catpic, name):
                print(f"  ✓ {name}")
            else:
                print(f"  ✗ {name} - NOT FOUND")
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        print(f"✗ Failed to check exports: {e}")
        traceback.print_exc()
        return False

def check_test_files():
    """Check if test files exist and are syntactically valid."""
    print("\n" + "=" * 60)
    print("CHECKING TEST FILES")
    print("=" * 60)
    
    test_dir = Path('tests')
    if not test_dir.exists():
        print(f"✗ Test directory not found: {test_dir}")
        return False
    
    test_files = list(test_dir.glob('test_*.py'))
    if not test_files:
        print(f"✗ No test files found in {test_dir}")
        return False
    
    all_ok = True
    for test_file in test_files:
        print(f"\n{test_file.name}:")
        try:
            # Check if file can be compiled (syntax check)
            with open(test_file) as f:
                code = f.read()
                compile(code, str(test_file), 'exec')
            print(f"  ✓ Syntax OK")
            
            # Try to import it
            module_name = test_file.stem
            sys.path.insert(0, str(test_dir))
            try:
                __import__(module_name)
                print(f"  ✓ Import OK")
            except Exception as e:
                print(f"  ✗ Import failed: {e}")
                if "--verbose" in sys.argv:
                    traceback.print_exc()
                all_ok = False
            finally:
                sys.path.pop(0)
                
        except SyntaxError as e:
            print(f"  ✗ Syntax error: {e}")
            all_ok = False
    
    return all_ok

def check_test_data():
    """Check if test data files exist."""
    print("\n" + "=" * 60)
    print("CHECKING TEST DATA")
    print("=" * 60)
    
    # Common test data locations
    data_paths = [
        Path('tests/data'),
        Path('tests/fixtures'),
        Path('test_data'),
    ]
    
    found_data_dir = None
    for path in data_paths:
        if path.exists():
            found_data_dir = path
            print(f"✓ Found test data directory: {path}")
            break
    
    if not found_data_dir:
        print("⚠ No test data directory found")
        print("  Tests may need sample images (JPEG, PNG, GIF)")
        return False
    
    # Check for common test files
    image_files = list(found_data_dir.glob('*.jpg')) + \
                  list(found_data_dir.glob('*.png')) + \
                  list(found_data_dir.glob('*.gif'))
    
    if image_files:
        print(f"✓ Found {len(image_files)} test image(s)")
        for img in image_files[:5]:  # Show first 5
            print(f"  - {img.name}")
    else:
        print("⚠ No test images found")
        return False
    
    return True

def check_environment():
    """Check environment variables."""
    print("\n" + "=" * 60)
    print("CHECKING ENVIRONMENT")
    print("=" * 60)
    
    import os
    
    catpic_basis = os.environ.get('CATPIC_BASIS')
    if catpic_basis:
        print(f"✓ CATPIC_BASIS={catpic_basis}")
    else:
        print("  CATPIC_BASIS not set (will use default: 2,2)")
    
    return True

def main():
    print("\nCatpic Test Diagnostics")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Working directory: {Path.cwd()}")
    print()
    
    results = []
    
    results.append(("Imports", check_imports()))
    results.append(("Exports", check_exports()))
    results.append(("Test Files", check_test_files()))
    results.append(("Test Data", check_test_data()))
    results.append(("Environment", check_environment()))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for name, ok in results:
        status = "✓" if ok else "✗"
        print(f"{status} {name}")
    
    all_ok = all(ok for _, ok in results)
    
    if all_ok:
        print("\n✓ All checks passed! Ready to run pytest.")
        return 0
    else:
        print("\n✗ Some checks failed. Fix issues before running pytest.")
        print("\nNext steps:")
        print("  1. Fix any import errors")
        print("  2. Ensure test files are syntactically correct")
        print("  3. Create test data if missing")
        print("  4. Run: uv run pytest -v")
        return 1

if __name__ == '__main__':
    sys.exit(main())
