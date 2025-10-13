> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LoadImageSetNode/en.md)

The LoadImageSetNode loads multiple images from the input directory for batch processing and training purposes. It supports various image formats and can optionally resize the images using different methods. This node processes all selected images as a batch and returns them as a single tensor.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `images` | IMAGE | Yes | Multiple image files | Select multiple images from the input directory. Supports PNG, JPG, JPEG, WEBP, BMP, GIF, JPE, APNG, TIF, and TIFF formats. Allows batch selection of images. |
| `resize_method` | STRING | No | "None"<br>"Stretch"<br>"Crop"<br>"Pad" | Optional method to resize loaded images (default: "None"). Choose "None" to keep original sizes, "Stretch" to force resize, "Crop" to maintain aspect ratio by cropping, or "Pad" to maintain aspect ratio by adding padding. |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `IMAGE` | IMAGE | A tensor containing all loaded images as a batch for further processing. |
