> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/FluxProExpandNode/en.md)

Outpaints image based on prompt. This node expands an image by adding pixels to the top, bottom, left, and right sides while generating new content that matches the provided text description.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `image` | IMAGE | Yes | - | The input image to be expanded |
| `prompt` | STRING | No | - | Prompt for the image generation (default: "") |
| `prompt_upsampling` | BOOLEAN | No | - | Whether to perform upsampling on the prompt. If active, automatically modifies the prompt for more creative generation, but results are nondeterministic (same seed will not produce exactly the same result). (default: False) |
| `top` | INT | No | 0-2048 | Number of pixels to expand at the top of the image (default: 0) |
| `bottom` | INT | No | 0-2048 | Number of pixels to expand at the bottom of the image (default: 0) |
| `left` | INT | No | 0-2048 | Number of pixels to expand at the left of the image (default: 0) |
| `right` | INT | No | 0-2048 | Number of pixels to expand at the right of the image (default: 0) |
| `guidance` | FLOAT | No | 1.5-100 | Guidance strength for the image generation process (default: 60) |
| `steps` | INT | No | 15-50 | Number of steps for the image generation process (default: 50) |
| `seed` | INT | No | 0-18446744073709551615 | The random seed used for creating the noise. (default: 0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `image` | IMAGE | The expanded output image |
