> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RecraftRemoveBackgroundNode/en.md)

This node removes the background from images using the Recraft API service. It processes each image in the input batch and returns both the processed images with transparent backgrounds and corresponding alpha masks that indicate the removed background areas.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `image` | IMAGE | Yes | - | The input image(s) to process for background removal |
| `auth_token` | STRING | No | - | Authentication token for Recraft API access |
| `comfy_api_key` | STRING | No | - | API key for Comfy.org service integration |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `image` | IMAGE | Processed images with transparent backgrounds |
| `mask` | MASK | Alpha channel masks indicating the removed background areas |
