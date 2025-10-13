> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StabilityUpscaleCreativeNode/en.md)

Upscale image with minimal alterations to 4K resolution. This node uses Stability AI's creative upscaling technology to enhance image resolution while preserving the original content and adding subtle creative details.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `image` | IMAGE | Yes | - | The input image to be upscaled |
| `prompt` | STRING | Yes | - | What you wish to see in the output image. A strong, descriptive prompt that clearly defines elements, colors, and subjects will lead to better results. (default: empty string) |
| `creativity` | FLOAT | Yes | 0.1-0.5 | Controls the likelihood of creating additional details not heavily conditioned by the init image. (default: 0.3) |
| `style_preset` | COMBO | Yes | Multiple options available | Optional desired style of generated image. Options include various style presets from Stability AI. |
| `seed` | INT | Yes | 0-4294967294 | The random seed used for creating the noise. (default: 0) |
| `negative_prompt` | STRING | No | - | Keywords of what you do not wish to see in the output image. This is an advanced feature. (default: empty string) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `image` | IMAGE | The upscaled image at 4K resolution |
