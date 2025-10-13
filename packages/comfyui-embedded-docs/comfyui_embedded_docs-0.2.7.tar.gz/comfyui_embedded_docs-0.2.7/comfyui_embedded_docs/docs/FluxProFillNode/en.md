> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/FluxProFillNode/en.md)

Inpaints image based on mask and prompt. This node uses the Flux.1 model to fill in masked areas of an image according to the provided text description, generating new content that matches the surrounding image.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `image` | IMAGE | Yes | - | The input image to be inpainted |
| `mask` | MASK | Yes | - | The mask defining which areas of the image should be filled |
| `prompt` | STRING | No | - | Prompt for the image generation (default: empty string) |
| `prompt_upsampling` | BOOLEAN | No | - | Whether to perform upsampling on the prompt. If active, automatically modifies the prompt for more creative generation, but results are nondeterministic (same seed will not produce exactly the same result). (default: false) |
| `guidance` | FLOAT | No | 1.5-100 | Guidance strength for the image generation process (default: 60) |
| `steps` | INT | No | 15-50 | Number of steps for the image generation process (default: 50) |
| `seed` | INT | No | 0-18446744073709551615 | The random seed used for creating the noise. (default: 0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output_image` | IMAGE | The generated image with the masked areas filled according to the prompt |
