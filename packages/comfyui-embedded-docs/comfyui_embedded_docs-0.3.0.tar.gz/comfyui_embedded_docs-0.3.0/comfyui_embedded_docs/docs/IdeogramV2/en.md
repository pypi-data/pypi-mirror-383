> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/IdeogramV2/en.md)

The Ideogram V2 node generates images using the Ideogram V2 AI model. It takes text prompts and various generation settings to create images through an API service. The node supports different aspect ratios, resolutions, and style options to customize the output images.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `prompt` | STRING | Yes | - | Prompt for the image generation (default: empty string) |
| `turbo` | BOOLEAN | No | - | Whether to use turbo mode (faster generation, potentially lower quality) (default: False) |
| `aspect_ratio` | COMBO | No | "1:1"<br>"16:9"<br>"9:16"<br>"4:3"<br>"3:4"<br>"3:2"<br>"2:3" | The aspect ratio for image generation. Ignored if resolution is not set to AUTO. (default: "1:1") |
| `resolution` | COMBO | No | "Auto"<br>"1024x1024"<br>"1152x896"<br>"896x1152"<br>"1216x832"<br>"832x1216"<br>"1344x768"<br>"768x1344"<br>"1536x640"<br>"640x1536" | The resolution for image generation. If not set to AUTO, this overrides the aspect_ratio setting. (default: "Auto") |
| `magic_prompt_option` | COMBO | No | "AUTO"<br>"ON"<br>"OFF" | Determine if MagicPrompt should be used in generation (default: "AUTO") |
| `seed` | INT | No | 0-2147483647 | Random seed for generation (default: 0) |
| `style_type` | COMBO | No | "AUTO"<br>"GENERAL"<br>"REALISTIC"<br>"DESIGN"<br>"RENDER_3D"<br>"ANIME" | Style type for generation (V2 only) (default: "NONE") |
| `negative_prompt` | STRING | No | - | Description of what to exclude from the image (default: empty string) |
| `num_images` | INT | No | 1-8 | Number of images to generate (default: 1) |

**Note:** When `resolution` is not set to "Auto", it overrides the `aspect_ratio` setting. The `num_images` parameter has a maximum limit of 8 images per generation.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | IMAGE | The generated image(s) from the Ideogram V2 model |
