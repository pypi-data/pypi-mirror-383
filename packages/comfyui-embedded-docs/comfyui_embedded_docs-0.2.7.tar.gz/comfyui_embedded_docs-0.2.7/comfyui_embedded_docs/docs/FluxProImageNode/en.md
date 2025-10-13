> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/FluxProImageNode/en.md)

Generates images synchronously based on prompt and resolution. This node creates images using the Flux 1.1 Pro model by sending requests to an API endpoint and waiting for the complete response before returning the generated image.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `prompt` | STRING | Yes | - | Prompt for the image generation (default: empty string) |
| `prompt_upsampling` | BOOLEAN | Yes | - | Whether to perform upsampling on the prompt. If active, automatically modifies the prompt for more creative generation, but results are nondeterministic (same seed will not produce exactly the same result). (default: False) |
| `width` | INT | Yes | 256-1440 | Image width in pixels (default: 1024, step: 32) |
| `height` | INT | Yes | 256-1440 | Image height in pixels (default: 768, step: 32) |
| `seed` | INT | Yes | 0-18446744073709551615 | The random seed used for creating the noise. (default: 0) |
| `image_prompt` | IMAGE | No | - | Optional reference image to guide the generation |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | IMAGE | The generated image returned from the API |
