> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LoadImageSetFromFolderNode/en.md)

The LoadImageSetFromFolderNode loads multiple images from a specified folder directory for training purposes. It automatically detects common image formats and can optionally resize the images using different methods before returning them as a batch.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `folder` | STRING | Yes | Multiple options available | The folder to load images from. |
| `resize_method` | STRING | No | "None"<br>"Stretch"<br>"Crop"<br>"Pad" | The method to use for resizing images (default: "None"). |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `IMAGE` | IMAGE | The batch of loaded images as a single tensor. |
