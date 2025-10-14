#!/bin/bash
set -e

# Build the wheel
python -m build --wheel

# Platform-specific wheel repair
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Running delocate-wheel for macOS..."
    delocate-wheel -w dist -v dist/*.whl
else
    echo "Running auditwheel for Linux..."
    # Find the wheel we just built (newest .whl file)
    WHEEL_FILE=$(ls -t dist/*.whl 2>/dev/null | head -1)

    # First check what platform the wheel is compatible with
    echo "Checking wheel compatibility..."
    auditwheel show "$WHEEL_FILE"

    # Repair with auto-detected tag first
    echo "Repairing wheel..."
    auditwheel repair "$WHEEL_FILE" -w dist

    # Remove the original unrepaired wheel
    rm -f dist/*-linux_x86_64.whl

    # Add multiple platform tags for broader compatibility
    echo "Adding multiple platform tags for UV compatibility..."
    for wheel in dist/*-manylinux_2_*_x86_64.whl; do
        if [ -f "$wheel" ]; then
            # Extract wheel
            tmpdir=$(mktemp -d)
            unzip -q "$wheel" -d "$tmpdir"

            # Get the current tag from the wheel name
            # Format: name-version-python-abi-platform.whl
            # Example: tdcsophiread-3.1.5-cp312-cp312-manylinux_2_34_x86_64.whl
            base_name=$(basename "$wheel" .whl)
            # Split by dash and get the parts
            IFS='-' read -ra PARTS <<< "$base_name"
            # Parts: [tdcsophiread, 3.1.5, cp312, cp312, manylinux_2_34_x86_64]
            python_tag="${PARTS[2]}"  # cp312
            abi_tag="${PARTS[3]}"      # cp312

            # Modify WHEEL file to add multiple tags
            wheel_file=$(find "$tmpdir" -name "WHEEL" -path "*.dist-info/*")

            # Remove existing Tag lines
            grep -v "^Tag:" "$wheel_file" > "$wheel_file.tmp"
            mv "$wheel_file.tmp" "$wheel_file"

            # Add multiple platform tags in order of specificity
            # If wheel is manylinux_2_34, it's also compatible with 2.28, 2.17, etc.
            if [[ "$wheel" == *"manylinux_2_39"* ]] || [[ "$wheel" == *"manylinux_2_34"* ]]; then
                echo "Tag: ${python_tag}-${abi_tag}-manylinux_2_34_x86_64" >> "$wheel_file"
                echo "Tag: ${python_tag}-${abi_tag}-manylinux_2_28_x86_64" >> "$wheel_file"
                echo "Tag: ${python_tag}-${abi_tag}-manylinux_2_17_x86_64" >> "$wheel_file"
                echo "Tag: ${python_tag}-${abi_tag}-manylinux2014_x86_64" >> "$wheel_file"
            elif [[ "$wheel" == *"manylinux_2_28"* ]]; then
                echo "Tag: ${python_tag}-${abi_tag}-manylinux_2_28_x86_64" >> "$wheel_file"
                echo "Tag: ${python_tag}-${abi_tag}-manylinux_2_17_x86_64" >> "$wheel_file"
                echo "Tag: ${python_tag}-${abi_tag}-manylinux2014_x86_64" >> "$wheel_file"
            elif [[ "$wheel" == *"manylinux_2_17"* ]] || [[ "$wheel" == *"manylinux2014"* ]]; then
                echo "Tag: ${python_tag}-${abi_tag}-manylinux_2_17_x86_64" >> "$wheel_file"
                echo "Tag: ${python_tag}-${abi_tag}-manylinux2014_x86_64" >> "$wheel_file"
            else
                # Keep original tag if we don't recognize the pattern
                echo "Tag: ${python_tag}-${abi_tag}-$(echo "$base_name" | cut -d'-' -f4)" >> "$wheel_file"
            fi

            # Show what tags we're adding before repacking
            echo "Added multiple tags to: $(basename "$wheel")"
            echo "Tags added:"
            grep "^Tag:" "$wheel_file" | tail -5

            # Repack the wheel
            rm "$wheel"
            (cd "$tmpdir" && zip -q -r - .) > "$wheel"
            rm -rf "$tmpdir"
        fi
    done
fi

echo "Wheel build complete with multiple platform tags!"