import os
from image_tools import blur_image, grayscale_image, resize_image

def test_processing():
    input_path = "tests/sample.jpg"
    blur_image(input_path, "tests/blur.jpg")
    grayscale_image(input_path, "tests/gray.jpg")
    resize_image(input_path, "tests/resized.jpg", 100, 100)
    assert os.path.exists("tests/blur.jpg")
    assert os.path.exists("tests/gray.jpg")
    assert os.path.exists("tests/resized.jpg")
