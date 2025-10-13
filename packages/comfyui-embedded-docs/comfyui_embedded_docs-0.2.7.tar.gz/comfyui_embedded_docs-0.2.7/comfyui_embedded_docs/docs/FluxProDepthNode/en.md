> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/FluxProDepthNode/en.md)

This node generates images using a depth control image as guidance. It takes a control image and a text prompt, then creates a new image that follows both the depth information from the control image and the description in the prompt. The node connects to an external API to perform the image generation process.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `control_image` | IMAGE | Yes | - | The depth control image used to guide the image generation |
| `prompt` | STRING | No | - | Prompt for the image generation (default: empty string) |
| `prompt_upsampling` | BOOLEAN | No | - | Whether to perform upsampling on the prompt. If active, automatically modifies the prompt for more creative generation, but results are nondeterministic (same seed will not produce exactly the same result). (default: False) |
| `skip_preprocessing` | BOOLEAN | No | - | Whether to skip preprocessing; set to True if control_image already is depth-ified, False if it is a raw image. (default: False) |
| `guidance` | FLOAT | No | 1-100 | Guidance strength for the image generation process (default: 15) |
| `steps` | INT | No | 15-50 | Number of steps for the image generation process (default: 50) |
| `seed` | INT | No | 0-18446744073709551615 | The random seed used for creating the noise. (default: 0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output_image` | IMAGE | The generated image based on the depth control image and prompt |
