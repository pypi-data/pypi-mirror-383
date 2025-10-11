from PIL import Image

def resize_image(input_path: str, output_path: str, width: int, height: int):
    img = Image.open(input_path)
    img = img.resize((width, height))
    img.save(output_path)
