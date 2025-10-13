> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ByteDanceImageNode/en.md)

The ByteDance Image node generates images using ByteDance models through an API based on text prompts. It allows you to select different models, specify image dimensions, and control various generation parameters like seed and guidance scale. The node connects to ByteDance's image generation service and returns the created image.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `model` | MODEL | COMBO | seedream_3 | Text2ImageModelName options | Model name |
| `prompt` | STRING | STRING | - | - | The text prompt used to generate the image |
| `size_preset` | STRING | COMBO | - | RECOMMENDED_PRESETS labels | Pick a recommended size. Select Custom to use the width and height below |
| `width` | INT | INT | 1024 | 512-2048 (step 64) | Custom width for image. Value is working only if `size_preset` is set to `Custom` |
| `height` | INT | INT | 1024 | 512-2048 (step 64) | Custom height for image. Value is working only if `size_preset` is set to `Custom` |
| `seed` | INT | INT | 0 | 0-2147483647 (step 1) | Seed to use for generation (optional) |
| `guidance_scale` | FLOAT | FLOAT | 2.5 | 1.0-10.0 (step 0.01) | Higher value makes the image follow the prompt more closely (optional) |
| `watermark` | BOOLEAN | BOOLEAN | True | - | Whether to add an "AI generated" watermark to the image (optional) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `IMAGE` | IMAGE | The generated image from the ByteDance API |
