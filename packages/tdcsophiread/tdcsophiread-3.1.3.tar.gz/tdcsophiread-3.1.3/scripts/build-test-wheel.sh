#!/bin/bash
set -e

# Script to build and test a Python wheel for a specific Python version
# Usage: ./scripts/build-test-wheel.sh py310|py311|py312|py313|py314

if [ $# -ne 1 ]; then
    echo "Usage: $0 <python-environment>"
    echo "Example: $0 py312"
    exit 1
fi

PYENV=$1
PYVER=${PYENV#py}  # Extract version number (e.g., 310 from py310)
PYVER_DISPLAY="3.${PYVER:1}"  # Convert 310 → 3.10, 314 → 3.14
REPO_ROOT=$(pwd)

echo "========================================"
echo "Building wheel for Python $PYVER_DISPLAY"
echo "========================================"

# Step 1: Clean build artifacts
echo "Step 1: Cleaning build artifacts..."
rm -rf build dist

# Step 2: Build wheel in the specified environment
echo "Step 2: Building wheel..."
pixi run --environment $PYENV build-wheel

# Verify wheel was created
WHEEL_FILE=$(ls dist/*.whl 2>/dev/null | head -1)
if [ -z "$WHEEL_FILE" ]; then
    echo "ERROR: No wheel file found in dist/"
    exit 1
fi
WHEEL_FILE=$(readlink -f "$WHEEL_FILE")  # Convert to absolute path
echo "Built: $(basename $WHEEL_FILE)"

# Step 3: Test wheel in clean environment
echo "Step 3: Testing wheel in clean environment..."
TEST_DIR="/tmp/test_wheel_${PYENV}_$$"
rm -rf $TEST_DIR
mkdir -p $TEST_DIR
cd $TEST_DIR

# Create clean pixi environment
pixi init --platform linux-64 > /dev/null 2>&1
pixi add python=${PYVER_DISPLAY}.* pip > /dev/null 2>&1

# Install the wheel
echo "Installing wheel..."
if ! pixi run pip install $WHEEL_FILE > /tmp/pip_install_$$.log 2>&1; then
    echo "ERROR: Failed to install wheel"
    cat /tmp/pip_install_$$.log
    rm -f /tmp/pip_install_$$.log
    exit 1
fi
rm -f /tmp/pip_install_$$.log

# Test import and verify version
echo "Testing import and version..."
if ! INSTALLED_VERSION=$(pixi run python -c 'import tdcsophiread; print(tdcsophiread.__version__)' 2>&1); then
    echo "ERROR: Failed to import tdcsophiread"
    echo "$INSTALLED_VERSION"
    exit 1
fi

# Extract expected version from pyproject.toml
cd $REPO_ROOT
EXPECTED_VERSION=$(grep '^version = ' pyproject.toml | head -1 | sed 's/version = "\(.*\)"/\1/')

if [ "$INSTALLED_VERSION" != "$EXPECTED_VERSION" ]; then
    echo "ERROR: Version mismatch!"
    echo "  Expected: $EXPECTED_VERSION"
    echo "  Got:      $INSTALLED_VERSION"
    exit 1
fi

echo "✓ Test passed: version $INSTALLED_VERSION"

# Step 4: Move to final distribution directory
echo "Step 4: Collecting wheel..."
mkdir -p dist-wheels
cp $WHEEL_FILE dist-wheels/
echo "✓ Wheel saved to dist-wheels/$(basename $WHEEL_FILE)"

# Cleanup
cd $REPO_ROOT
rm -rf $TEST_DIR

echo "========================================"
echo "Successfully built and tested Python $PYVER_DISPLAY wheel"
echo "========================================"
