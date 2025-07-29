import subprocess
import os
import pytest
from PIL import Image, ImageChops

# Define constants for test data and output directory
TEST_BAM1 = "test/test_tumor.bam"  # Replace with actual test BAM file
TEST_BAM2 = "test/test_normal.bam"  # Replace with actual test BAM file
OUTPUT_DIR = "test/output"
TMP_DIR = os.environ.get('TMPDIR', '/tmp')
os.makedirs(OUTPUT_DIR, exist_ok=True)
REGION = "8:32534767-32536767 19:11137898-11139898"
FILENAME = "8-32534767-32536767.19-11137898-11139898.translocation.tumor.png"
EXPECTED_IMAGE = os.path.join(OUTPUT_DIR, FILENAME.replace('.translocation', ''))
BASELINE_IMAGE = os.path.join("test/snapshots", FILENAME)  # Pre-generated baseline image
SINGULARITY_IMAGE = "docker://quay.io/soymintc/igver"
#  SINGULARITY_IMAGE = "/data1/shahs3/users/chois7/singularity/sifs/igver-latest.sif"
SINGULARITY_BIND_DIR = os.path.abspath(".")

@pytest.fixture(scope="function", autouse=True)
def setup_cleanup():
    """Fixture to clean up generated files after test."""
    yield
    if os.path.exists(EXPECTED_IMAGE):
        os.remove(EXPECTED_IMAGE)

def test_png_generation():
    """Test if igver generates a PNG correctly from the command line."""
    command = [
	'singularity', 'run', 
        '-B', SINGULARITY_BIND_DIR,
        '-B', TMP_DIR,
        SINGULARITY_IMAGE,
        'python', 'igver.py',
        '--bam', TEST_BAM1, TEST_BAM2,
        '-r', REGION,
        '-o', OUTPUT_DIR,
        '-g', 'hg19'
    ]
    print(" ".join(command))

    result = subprocess.run(command, capture_output=True, text=True)

    # Ensure the command runs successfully
    assert result.returncode == 0, f"Command failed: {result.stderr}"

    # Verify the PNG file was created
    assert os.path.exists(EXPECTED_IMAGE), "PNG file was not created."

def test_image_integrity():
    """Check if the generated PNG file is a valid image."""
    test_png_generation()  # Ensure the PNG file is generated
    try:
        with Image.open(EXPECTED_IMAGE) as img:
            img.verify()  # Verifies the integrity
    except (IOError, SyntaxError) as e:
        pytest.fail(f"Generated PNG file is corrupted: {e}")

def test_image_comparison():
    """Compare the generated PNG file with a baseline image."""
    test_png_generation()  # Ensure the PNG file is generated
    assert os.path.exists(BASELINE_IMAGE), "Baseline image not found."

    def images_are_equal(img1_path, img2_path):
        with Image.open(img1_path) as img1, Image.open(img2_path) as img2:
            return ImageChops.difference(img1, img2).getbbox() is None

    assert images_are_equal(EXPECTED_IMAGE, BASELINE_IMAGE), "Generated image differs from the baseline."

