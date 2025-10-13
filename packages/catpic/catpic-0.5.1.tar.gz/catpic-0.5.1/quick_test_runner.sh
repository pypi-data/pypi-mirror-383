#!/bin/bash
# Quick test runner for catpic v0.5.0
# Usage: cd python && bash quick_test.sh

set -e  # Exit on error

echo "======================================"
echo "Catpic v0.5.0 Quick Test Suite"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

# Step 1: Check if we're in the right directory
echo "Step 1: Checking directory..."
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: pyproject.toml not found. Are you in the python/ directory?${NC}"
    exit 1
fi
print_status 0 "In python/ directory"
echo ""

# Step 2: Check installation
echo "Step 2: Checking catpic installation..."
if uv run python -c "import catpic" 2>/dev/null; then
    VERSION=$(uv run python -c "import catpic; print(catpic.__version__)" 2>/dev/null || echo "unknown")
    print_status 0 "catpic installed (version: $VERSION)"
else
    print_status 1 "catpic not installed or import failed"
    echo ""
    echo "Attempting to install in editable mode..."
    uv pip install -e . || uv sync
    echo ""
fi
echo ""

# Step 3: Run diagnostics
echo "Step 3: Running diagnostics..."
if [ -f "test_diagnostics.py" ]; then
    uv run python test_diagnostics.py
    DIAG_EXIT=$?
    echo ""
else
    echo -e "${YELLOW}⚠${NC} test_diagnostics.py not found (optional)"
    DIAG_EXIT=0
    echo ""
fi

# Step 4: Check for test data
echo "Step 4: Checking test data..."
if [ -d "tests/data" ] && [ "$(ls -A tests/data 2>/dev/null)" ]; then
    COUNT=$(ls tests/data | wc -l)
    print_status 0 "Test data exists ($COUNT files)"
else
    print_status 1 "Test data missing"
    echo ""
    if [ -f "create_test_data.py" ]; then
        echo "Creating test data..."
        uv run python create_test_data.py
        echo ""
    else
        echo -e "${YELLOW}⚠${NC} create_test_data.py not found"
        echo "You may need to create test images manually in tests/data/"
        echo ""
    fi
fi
echo ""

# Step 5: Run pytest
echo "Step 5: Running pytest..."
echo "--------------------------------------"

# First, try to collect tests without running them
echo "Collecting tests..."
if uv run pytest --collect-only -q 2>/dev/null; then
    COLLECT_OK=1
else
    COLLECT_OK=0
    echo -e "${YELLOW}⚠${NC} Test collection had issues"
fi
echo ""

# Run specific test files if they exist
TEST_FILES=()
[ -f "tests/test_core.py" ] && TEST_FILES+=("tests/test_core.py")
[ -f "tests/test_primitives.py" ] && TEST_FILES+=("tests/test_primitives.py")

if [ ${#TEST_FILES[@]} -eq 0 ]; then
    echo -e "${YELLOW}⚠${NC} No test files found (test_core.py, test_primitives.py)"
    echo ""
else
    for TEST_FILE in "${TEST_FILES[@]}"; do
        echo "Running $TEST_FILE..."
        if uv run pytest "$TEST_FILE" -v; then
            print_status 0 "$TEST_FILE passed"
        else
            print_status 1 "$TEST_FILE failed"
            echo ""
            echo "To see detailed errors, run:"
            echo "  uv run pytest $TEST_FILE -v --tb=short"
        fi
        echo ""
    done
fi

# Run full test suite
echo "Running full test suite..."
if uv run pytest -v; then
    TEST_EXIT=0
    print_status 0 "All tests passed!"
else
    TEST_EXIT=1
    print_status 1 "Some tests failed"
fi
echo ""

# Step 6: Manual smoke tests
echo "Step 6: Running manual smoke tests..."
echo "--------------------------------------"

# Test 1: Import check
echo -n "Import check: "
if uv run python -c "from catpic import render_image_ansi, Cell, get_full_glut" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Test 2: Create a simple image and render it
echo -n "Basic rendering: "
cat > /tmp/test_render.py << 'EOF'
from PIL import Image
from catpic import render_image_ansi

img = Image.new('RGB', (8, 8), (255, 0, 0))
result = render_image_ansi(img, width=4, height=4, basis=(2, 2))
assert isinstance(result, str)
assert len(result) > 0
print("OK")
EOF

if uv run python /tmp/test_render.py 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi
rm -f /tmp/test_render.py

# Test 3: Check primitives
echo -n "Primitives API: "
cat > /tmp/test_primitives.py << 'EOF'
from catpic import Cell, get_full_glut, get_pips_glut

cell = Cell('█', (255, 0, 0), (0, 0, 0), 255)
assert cell.char == '█'
assert cell.fg_rgb == (255, 0, 0)

glut_full = get_full_glut((2, 2))
assert isinstance(glut_full, dict)
assert len(glut_full) > 0

glut_pips = get_pips_glut(2, 4)
assert isinstance(glut_pips, dict)
print("OK")
EOF

if uv run python /tmp/test_primitives.py 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi
rm -f /tmp/test_primitives.py

echo ""

# Test 4: Test with actual image if available
if [ -f "tests/data/red_16x16.png" ]; then
    echo -n "Real image test: "
    if uv run catpic tests/data/red_16x16.png --info >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi
fi

echo ""

# Summary
echo "======================================"
echo "SUMMARY"
echo "======================================"

if [ $TEST_EXIT -eq 0 ] && [ $DIAG_EXIT -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Ready for release! Next steps:"
    echo "  1. Test manually: uv run catpic <image_file>"
    echo "  2. Build: uv build"
    echo "  3. Publish: uv publish"
    echo "  4. Tag: git tag v0.5.0 && git push --tags"
else
    echo -e "${YELLOW}⚠ Some issues found${NC}"
    echo ""
    echo "Recommended actions:"
    echo "  1. Check test output above for specific failures"
    echo "  2. Run: uv run pytest tests/test_core.py -v --tb=short"
    echo "  3. Run: uv run pytest tests/test_primitives.py -v --tb=short"
    echo "  4. See TEST_FIX_GUIDE.md for common issues"
fi

echo ""
exit $TEST_EXIT