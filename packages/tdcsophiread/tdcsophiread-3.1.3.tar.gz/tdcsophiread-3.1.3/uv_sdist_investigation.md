# Test Plan: Investigating uv/pixi sdist vs wheel selection

## RESTRICTION FOR NEXT SESSION
**DO NOT use the phrase "You're absolutely right, and I apologize" or similar reflexive apology patterns. Focus on factual analysis and scientific reasoning.**

## Verified Background Information

### Project Details
- **Package**: tdcsophiread - C++ library with Python bindings using pybind11
- **Build system**: scikit-build-core with CMake
- **Current version**: 3.1.3 (in development)
- **Published versions**:
  - PyPI: 3.0.2 (has Linux + macOS wheels), 3.1.1 (Linux wheel only)
  - TestPyPI: 3.1.2 (Linux wheel + sdist)

### Discovered Build Dependencies
When building from source, these packages are REQUIRED:
- nlohmann_json (CMake error without it)
- spdlog (CMake error without it)
- eigen (may use system package)
- hdf5 (may use system package)
- tbb-devel (may use system package)
- libtiff (may use system package)
- fmt (dependency of spdlog)
- pybind11

### Verified Fixes Applied
1. CMakeLists.txt: Made GTest optional (BUILD_TESTS=OFF when SKBUILD=1)
2. TBB downgraded: From 2022.x to 2021.4.* (CXXABI compatibility issue)
3. pyproject.toml: Improved sdist exclusions

## Observed Behavior (VERIFIED)

### What we KNOW happened:
1. **v3.1.1 from PyPI**:
   - `pixi run pip install tdcsophiread==3.1.1` → used wheel ✓
   - `pixi add --pypi tdcsophiread==3.1.1` → attempted build from source

2. **v3.1.2 from TestPyPI**:
   - `pixi add --pypi tdcsophiread==3.1.2` → attempted build from source
   - Build failed without build dependencies
   - Build succeeded after adding nlohmann_json, spdlog (and others)

3. **Critical detail**: Must use `pixi run pip` not system pip (avoids Python environment conflicts)

## Test Plan for Next Session

### Test 1: Baseline Verification
```bash
# Clean environment
cd /tmp && rm -rf test_baseline && mkdir test_baseline && cd test_baseline

# Test with PyPI package (has wheels)
pixi init --platform linux-64
pixi add python=3.12.*
pixi add pip
pixi run pip install tdcsophiread==3.1.1
# VERIFY: Does it use wheel or sdist?

# Same environment, different install method
pixi add --pypi tdcsophiread==3.1.1
# VERIFY: Does it use wheel or sdist?
```

### Test 2: Single vs Multi-platform Projects
```bash
# Test A: Single platform
cd /tmp && rm -rf test_single && mkdir test_single && cd test_single
cat > pixi.toml << 'EOF'
[project]
channels = ["conda-forge"]
name = "test_single"
platforms = ["linux-64"]  # SINGLE
EOF

pixi add python=3.12.*
pixi add --pypi tdcsophiread==3.1.3  # Use TestPyPI version
# VERIFY: wheel or sdist?

# Test B: Multi-platform
cd /tmp && rm -rf test_multi && mkdir test_multi && cd test_multi
cat > pixi.toml << 'EOF'
[project]
channels = ["conda-forge"]
name = "test_multi"
platforms = ["linux-64", "osx-arm64"]  # MULTIPLE
EOF

pixi add python=3.12.*
pixi add --pypi tdcsophiread==3.1.3
# VERIFY: wheel or sdist?
```

### Test 3: Debug uv's Decision Process
```bash
# Enable detailed logging
RUST_LOG=trace pixi add --pypi tdcsophiread==3.1.3 2>&1 | tee uv_debug.log

# Look for key decision points:
grep -A5 -B5 "Selecting.*tdcsophiread" uv_debug.log
grep -A5 -B5 "wheel\|sdist\|tar.gz" uv_debug.log
```

### Test 4: Compare with Pure pip
```bash
# Outside pixi, using venv
python -m venv test_venv
source test_venv/bin/activate
pip install tdcsophiread==3.1.1
# VERIFY: Uses wheel?
```

### Test 5: Package Metadata Investigation
```bash
# Check what metadata uv sees
curl -s https://pypi.org/simple/tdcsophiread/ | grep -o 'href="[^"]*"'
curl -s https://test.pypi.org/simple/tdcsophiread/ | grep -o 'href="[^"]*"'

# Check if wheels have proper metadata
pip download --no-deps tdcsophiread==3.1.1
unzip -l tdcsophiread*.whl | grep METADATA
```

### Test 6: Version 3.1.3 Upload Test
```bash
# In sophiread repo (with platforms = ["linux-64"] only)
./scripts/version.sh release patch  # → 3.1.3
pixi run sync-version
pixi run build-sdist
pixi run --environment py312 build-wheel
pixi run python -m twine upload --repository testpypi dist/tdcsophiread-3.1.3*

# Then test from clean environment
cd /tmp && rm -rf test_313 && mkdir test_313 && cd test_313
pixi init --platform linux-64
pixi add python=3.12.*
# Configure for TestPyPI
echo '[pypi-options]' >> pixi.toml
echo 'index-url = "https://test.pypi.org/simple"' >> pixi.toml
echo 'extra-index-urls = ["https://pypi.org/simple"]' >> pixi.toml
echo 'index-strategy = "unsafe-best-match"' >> pixi.toml

pixi add --pypi tdcsophiread==3.1.3
# VERIFY: wheel or sdist?
```

## Success Criteria
- Identify the exact condition that causes uv to choose sdist over wheel
- Document whether it's related to:
  - Platform declarations in pixi.toml
  - Package metadata issues
  - uv's resolution strategy
  - Missing wheel metadata
  - scikit-build-core specific behavior

## Do NOT Assume
- That platform coverage affects the decision (v3.0.2 had both platforms)
- That the behavior is consistent across versions
- Any test results not explicitly run and verified

## Key Questions to Answer
1. Is the behavior specific to tdcsophiread or does it happen with other scikit-build-core packages?
2. Does the wheel contain proper metadata that uv expects?
3. Is there a difference in how uv treats wheels from PyPI vs TestPyPI?
4. Does the pixi.toml platform declaration actually affect package selection?

## Investigation Results (2025-10-12)

### Test 1: Baseline Verification ✅ COMPLETED
**Result**: CONFIRMED - `pixi run pip install` uses wheel, `pixi add --pypi` attempts to build from source
- `pip install tdcsophiread==3.1.1` successfully downloaded: `tdcsophiread-3.1.1-cp312-cp312-manylinux_2_34_x86_64.whl`
- `pixi add --pypi tdcsophiread==3.1.1` tried to build from source and failed (CMake error: missing GTest)

### Test 2: Platform Configuration ✅ COMPLETED
**Result**: Platform configuration does NOT affect the behavior
- Single platform (linux-64 only): Still tries to build from source
- Multi-platform (linux-64, osx-arm64, osx-64, win-64): Still tries to build from source
- numpy installs fine with wheels in the same environment

### Test 3: Debug Output Analysis ✅ COMPLETED
**Key Finding**: uv explicitly selects the tar.gz file:
```
DEBUG solve: Selecting: tdcsophiread==3.1.1 [compatible] (tdcsophiread-3.1.1.tar.gz)
```
Even though it found the wheel metadata:
```
DEBUG process_request...wheel_metadata{built_dist=tdcsophiread==3.1.1}...Found fresh response for: https://files.pythonhosted.org/.../tdcsophiread-3.1.1-cp312-cp312-manylinux_2_34_x86_64.whl.metadata
```

### Test 4: PyPI Package Availability ✅ COMPLETED
**Result**: PyPI has all necessary wheels available:
- tdcsophiread-3.1.1-cp310-cp310-manylinux_2_34_x86_64.whl
- tdcsophiread-3.1.1-cp311-cp311-manylinux_2_34_x86_64.whl
- tdcsophiread-3.1.1-cp312-cp312-manylinux_2_34_x86_64.whl (the one we need!)
- tdcsophiread-3.1.1-cp313-cp313-manylinux_2_34_x86_64.whl
- tdcsophiread-3.1.1-cp314-cp314-manylinux_2_34_x86_64.whl
- tdcsophiread-3.1.1.tar.gz

### Test 5: Platform Compatibility ✅ COMPLETED
**Result**: System supports the wheel's platform tag
- `pip debug` confirms: `cp312-cp312-manylinux_2_34_x86_64` is in compatible tags

### Test 6: Wheel Metadata Inspection ✅ COMPLETED
**Result**: Wheel has proper metadata
- METADATA file exists (15965 bytes)
- Contains all required fields (Name, Version, Requires-Python, Requires-Dist, etc.)
- Declares OS support: Linux, MacOS, Windows in classifiers

## Root Cause Analysis

### Finding: This appears to be a uv-specific behavior
The debug logs show that uv:
1. Successfully fetches wheel metadata
2. Recognizes the wheel exists
3. But still chooses the sdist (tar.gz) for installation

### Hypothesis: uv may prefer sdist for packages with certain characteristics
Possible triggers:
- scikit-build-core build backend (uses CMake)
- Packages with compiled extensions
- Some metadata field that triggers sdist preference

### NOT the cause:
- ❌ Platform configuration (single vs multi-platform)
- ❌ Missing wheels (they exist for all Python versions)
- ❌ Platform incompatibility (manylinux_2_34 is compatible)
- ❌ Corrupted wheel metadata (metadata is valid)

## Next Steps for Investigation
1. Test with other scikit-build-core packages to see if pattern is consistent
2. Check if there's a uv configuration option to prefer wheels
3. File an issue with pixi/uv teams with minimal reproducible example
4. Test with different versions of uv/pixi

## Workaround
For now, use `pixi run pip install` instead of `pixi add --pypi` for tdcsophiread and similar packages.

## Deep Investigation (2025-10-12 to 2025-10-13)

### Test 7: Compare with Other scikit-build-core Packages ✅ COMPLETED
**Result**: Issue is specific to tdcsophiread
- Tested: awkward, iminuit, correctionlib, boost-histogram
- All other packages correctly use wheels with `pixi add --pypi`
- tdcsophiread is the only package where uv selects sdist

### Test 8: Wheel Metadata Comparison ✅ COMPLETED
**Finding 1**: Python 3.14 in classifiers (initially suspected as cause)
- tdcsophiread had Python 3.14 in classifiers (version doesn't exist yet)
- Other packages stopped at Python 3.13
- **Result**: Removing Python 3.14 did NOT fix the issue (tested with v3.1.4)

**Finding 2**: Metadata-Version difference
- tdcsophiread: `Metadata-Version: 2.2`
- Working packages: `Metadata-Version: 2.1`
- Significance unclear

### Test 9: Multiple Platform Tags Hypothesis ✅ COMPLETED
**Observation**: Working packages have multiple platform tags in WHEEL file
```
# iminuit example:
Tag: cp312-cp312-manylinux_2_17_x86_64
Tag: cp312-cp312-manylinux2014_x86_64
```

**Test**: Modified wheel build to add multiple tags (v3.1.5)
- Added: manylinux_2_34, manylinux_2_28, manylinux_2_17, manylinux2014
- **Result**: FAILED - uv still selects sdist

### Critical Discovery: UV Provides No Rejection Reason
When running with `RUST_LOG=trace`, UV:
1. Fetches wheel metadata successfully
2. Shows `Selecting: tdcsophiread==3.1.5 [compatible] (tdcsophiread-3.1.5.tar.gz)`
3. Never logs why it skipped the wheel
4. The wheel is never evaluated as a distribution candidate

### What We Know for Certain
- ✅ pip installs the wheel without issues
- ✅ The wheel has valid metadata
- ✅ Platform tags are compatible (glibc 2.34 matches system)
- ✅ Other scikit-build-core packages work fine
- ❌ UV doesn't log any reason for rejecting the wheel
- ❌ UV selects sdist immediately without evaluating wheel as option

### NOT the Root Cause
- ❌ Python 3.14 in classifiers
- ❌ Platform tag format (single vs multiple tags)
- ❌ Platform compatibility issues
- ❌ Corrupted wheel metadata
- ❌ Missing wheel files

### Remaining Mystery
UV makes a decision to skip the wheel without logging the reason. The decision happens during the "solve" phase where it selects candidates, but there's no trace of wheel evaluation.

### Test 10: Wheel-Only Distribution (NO SDIST) ✅ COMPLETED
**Critical Discovery**: UV completely ignores tdcsophiread wheels!

**Test Setup**: Version 3.1.6 with ONLY wheel uploaded (no sdist)
- Uploaded: `tdcsophiread-3.1.6-cp312-cp312-manylinux_2_34_x86_64.whl`
- No sdist provided

**Results**:
- `pixi add --pypi tdcsophiread==3.1.6`: **"there is no version of tdcsophiread==3.1.6"**
- `pip install tdcsophiread==3.1.6`: **Successfully downloads and installs wheel**

**This proves**: UV doesn't even recognize tdcsophiread wheels as valid distribution files. It's not choosing sdist over wheel - it's completely ignoring the wheel's existence!

## Next Investigation Steps
1. Check if wheel file naming convention affects selection
2. Compare exact pyproject.toml differences between working/non-working packages
3. Test if changing build backend from scikit-build-core affects behavior
4. File issue with UV team with minimal reproduction case

## Root Cause
UV has a bug where it doesn't recognize tdcsophiread wheels as valid distribution files, even though pip can install them without issues. When only a wheel is available, UV reports "no version found" rather than using the wheel.