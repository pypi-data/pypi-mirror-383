from PIL import Image, ImageFilter

def blur_image(input_path: str, output_path: str, radius: int = 2):
    img = Image.open(input_path)
    img = img.filter(ImageFilter.GaussianBlur(radius))
    img.save(output_path)

def grayscale_image(input_path: str, output_path: str):
    img = Image.open(input_path)
    img = img.convert("L")
    img.save(output_path)
