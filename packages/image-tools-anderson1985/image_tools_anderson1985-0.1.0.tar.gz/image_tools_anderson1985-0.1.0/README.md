# image_tools

Pacote simples para processamento de imagens em Python.

## Funcionalidades
- Desfoque (blur)
- Conversão para tons de cinza
- Redimensionamento

## Instalação
```bash
pip install image_tools
```

## Exemplo de uso
```python
from image_tools import blur_image, grayscale_image, resize_image

blur_image("input.jpg", "blur.jpg", radius=3)
grayscale_image("input.jpg", "gray.jpg")
resize_image("input.jpg", "resized.jpg", 200, 200)
```
