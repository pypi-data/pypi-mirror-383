> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/IdeogramV1/en.md)

The IdeogramV1 node generates images using the Ideogram V1 model through an API. It takes text prompts and various generation settings to create one or more images based on your input. The node supports different aspect ratios and generation modes to customize the output.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `prompt` | STRING | Yes | - | Prompt for the image generation (default: empty) |
| `turbo` | BOOLEAN | Yes | - | Whether to use turbo mode (faster generation, potentially lower quality) (default: False) |
| `aspect_ratio` | COMBO | No | "1:1"<br>"16:9"<br>"9:16"<br>"4:3"<br>"3:4"<br>"3:2"<br>"2:3" | The aspect ratio for image generation (default: "1:1") |
| `magic_prompt_option` | COMBO | No | "AUTO"<br>"ON"<br>"OFF" | Determine if MagicPrompt should be used in generation (default: "AUTO") |
| `seed` | INT | No | 0-2147483647 | Random seed value for generation (default: 0) |
| `negative_prompt` | STRING | No | - | Description of what to exclude from the image (default: empty) |
| `num_images` | INT | No | 1-8 | Number of images to generate (default: 1) |

**Note:** The `num_images` parameter has a maximum limit of 8 images per generation request.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | IMAGE | The generated image(s) from the Ideogram V1 model |
