> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TextEncodeQwenImageEdit/en.md)

The TextEncodeQwenImageEdit node processes text prompts and optional images to generate conditioning data for image generation or editing. It uses a CLIP model to tokenize the input and can optionally encode reference images using a VAE to create reference latents. When an image is provided, it automatically resizes the image to maintain consistent processing dimensions.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `clip` | CLIP | Yes | - | The CLIP model used for text and image tokenization |
| `prompt` | STRING | Yes | - | Text prompt for conditioning generation, supports multiline input and dynamic prompts |
| `vae` | VAE | No | - | Optional VAE model for encoding reference images into latents |
| `image` | IMAGE | No | - | Optional input image for reference or editing purposes |

**Note:** When both `image` and `vae` are provided, the node encodes the image into reference latents and attaches them to the conditioning output. The image is automatically resized to maintain a consistent processing scale of approximately 1024x1024 pixels.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `CONDITIONING` | CONDITIONING | Conditioning data containing text tokens and optional reference latents for image generation |
