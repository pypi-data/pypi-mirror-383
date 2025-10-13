> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TextEncodeQwenImageEditPlus/en.md)

The TextEncodeQwenImageEditPlus node processes text prompts and optional images to generate conditioning data for image generation or editing tasks. It uses a specialized template to analyze input images and understand how text instructions should modify them, then encodes this information for use in subsequent generation steps. The node can handle up to three input images and optionally generate reference latents when a VAE is provided.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `clip` | CLIP | Yes | - | The CLIP model used for tokenization and encoding |
| `prompt` | STRING | Yes | - | Text instruction describing the desired image modification (supports multiline input and dynamic prompts) |
| `vae` | VAE | No | - | Optional VAE model for generating reference latents from input images |
| `image1` | IMAGE | No | - | First optional input image for analysis and modification |
| `image2` | IMAGE | No | - | Second optional input image for analysis and modification |
| `image3` | IMAGE | No | - | Third optional input image for analysis and modification |

**Note:** When a VAE is provided, the node generates reference latents from all input images. The node can process up to three images simultaneously, and images are automatically resized to appropriate dimensions for processing.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `CONDITIONING` | CONDITIONING | Encoded conditioning data containing text tokens and optional reference latents for image generation |
