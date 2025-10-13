> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LoadImageOutput/en.md)

The LoadImageOutput node loads images from the output folder. When you click the refresh button, it updates the list of available images and automatically selects the first one, making it easy to iterate through your generated images.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `image` | COMBO | Yes | Multiple options available | Load an image from the output folder. Includes an upload option and refresh button to update the image list. |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `image` | IMAGE | The loaded image from the output folder |
| `mask` | MASK | The mask associated with the loaded image |
