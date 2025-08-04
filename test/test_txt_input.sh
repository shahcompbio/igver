#!/bin/bash
# Test script for the new .txt file input feature

set -e  # Exit on error

echo "=== Testing igver with .txt file input ==="
echo

# Test directory
TEST_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="${TEST_DIR}/txt_input_test_output"
mkdir -p "$OUTPUT_DIR"

# Create a simple test input file if BAMs exist
if [ -f "${TEST_DIR}/test_tumor.bam" ] && [ -f "${TEST_DIR}/test_normal.bam" ]; then
    echo "Creating test input file..."
    cat > "${OUTPUT_DIR}/test_inputs.txt" << EOF
# Test input file
${TEST_DIR}/test_tumor.bam
${TEST_DIR}/test_normal.bam
EOF
    
    echo "Contents of test_inputs.txt:"
    cat "${OUTPUT_DIR}/test_inputs.txt"
    echo
    
    # Test 1: Using .txt file input with --no-singularity
    echo "Test 1: Running igver with .txt file input (--no-singularity mode)"
    echo "Command: igver -i ${OUTPUT_DIR}/test_inputs.txt -r \"8:32534767-32536767\" -o ${OUTPUT_DIR} -g hg19 --no-singularity"
    
    if command -v igver &> /dev/null; then
        igver -i "${OUTPUT_DIR}/test_inputs.txt" \
              -r "8:32534767-32536767" \
              -o "${OUTPUT_DIR}" \
              -g hg19 \
              --no-singularity \
              --debug || echo "Note: Command may fail if IGV is not installed locally"
    else
        echo "igver command not found. Running with python -m igver.cli"
        python -m igver.cli -i "${OUTPUT_DIR}/test_inputs.txt" \
                           -r "8:32534767-32536767" \
                           -o "${OUTPUT_DIR}" \
                           -g hg19 \
                           --no-singularity \
                           --debug || echo "Note: Command may fail if IGV is not installed locally"
    fi
    
    echo
    echo "Test 2: Using direct paths (backward compatibility test)"
    echo "Command: igver -i ${TEST_DIR}/test_tumor.bam ${TEST_DIR}/test_normal.bam -r \"8:32534767-32536767\" -o ${OUTPUT_DIR} -g hg19 --no-singularity"
    
    if command -v igver &> /dev/null; then
        igver -i "${TEST_DIR}/test_tumor.bam" "${TEST_DIR}/test_normal.bam" \
              -r "8:32534767-32536767" \
              -o "${OUTPUT_DIR}" \
              -g hg19 \
              --no-singularity \
              --debug || echo "Note: Command may fail if IGV is not installed locally"
    else
        python -m igver.cli -i "${TEST_DIR}/test_tumor.bam" "${TEST_DIR}/test_normal.bam" \
                           -r "8:32534767-32536767" \
                           -o "${OUTPUT_DIR}" \
                           -g hg19 \
                           --no-singularity \
                           --debug || echo "Note: Command may fail if IGV is not installed locally"
    fi
    
    echo
    echo "=== Tests completed ==="
    echo "Output directory: ${OUTPUT_DIR}"
    
else
    echo "Test BAM files not found. Creating a demo input file..."
    
    cat > "${OUTPUT_DIR}/demo_inputs.txt" << EOF
# Demo input file for igver
# Replace these paths with your actual BAM files

/path/to/sample1.bam
/path/to/sample2.bam
/path/to/sample3.bam

# You can also use home directory expansion
~/data/my_sample.bam
EOF
    
    echo "Created demo input file at: ${OUTPUT_DIR}/demo_inputs.txt"
    echo
    echo "To use this feature:"
    echo "1. Edit ${OUTPUT_DIR}/demo_inputs.txt with your actual BAM file paths"
    echo "2. Run: igver -i ${OUTPUT_DIR}/demo_inputs.txt -r \"chr1:1000-2000\" -o output_dir"
    echo
    echo "The new feature allows you to:"
    echo "- List multiple track files in a .txt file (one per line)"
    echo "- Add comments with # at the beginning of lines"
    echo "- Use empty lines for readability"
    echo "- Use ~ for home directory paths"
fi

# Clean up
echo
echo "Cleaning up test output directory..."
# Uncomment to clean up: rm -rf "$OUTPUT_DIR"