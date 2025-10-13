## Function Description

The EmptyImage node is used to create blank images with specified dimensions and colors. It can generate solid-color background images, commonly used as starting points or background images for image processing workflows.

## Working Principle

Just like a painter preparing a blank canvas before starting to create, the EmptyImage node provides you with a "digital canvas". You can specify the canvas size (width and height), choose the base color of the canvas, and even prepare multiple canvases of the same specifications at once. This node is like an intelligent art supply store that can create standardized canvases that perfectly meet your size and color requirements.

## Inputs

| Parameter Name | Data Type | Description |
|----------------|-----------|-------------|
| `width` | INT | Sets the width of the generated image (in pixels), determining the horizontal dimensions of the canvas |
| `height` | INT | Sets the height of the generated image (in pixels), determining the vertical dimensions of the canvas |
| `batch_size` | INT | The number of images to generate at once, used for batch creation of images with the same specifications |
| `color` | INT | The background color of the image. You can input hexadecimal color settings, which will be automatically converted to decimal |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `image` | IMAGE | The generated blank image tensor, formatted as [batch_size, height, width, 3], containing RGB three color channels |

## Common Color Reference Values

Since the current color input for this node is not user-friendly, with all color values being converted to decimal, here are some common color values that can be used directly for quick application.

| Color Name | Hexadecimal Value |
|------------|-------------------|
| Black      | 0x000000         |
| White      | 0xFFFFFF         |
| Red        | 0xFF0000         |
| Green      | 0x00FF00         |
| Blue       | 0x0000FF         |
| Yellow     | 0xFFFF00         |
| Cyan       | 0x00FFFF         |
| Magenta    | 0xFF00FF         |
| Orange     | 0xFF8000         |
| Purple     | 0x8000FF         |
| Pink       | 0xFF80C0         |
| Brown      | 0x8B4513         |
| Dark Gray  | 0x404040         |
| Light Gray | 0xC0C0C0         |
| Navy Blue  | 0x000080         |
| Dark Green | 0x008000         |
| Dark Red   | 0x800000         |
| Gold       | 0xFFD700         |
| Silver     | 0xC0C0C0         |
| Beige      | 0xF5F5DC         |
