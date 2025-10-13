> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RecraftImageToImageNode/en.md)

This node modifies an existing image based on a text prompt and strength parameter. It uses the Recraft API to transform the input image according to the provided description while maintaining some similarity to the original image based on the strength setting.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `image` | IMAGE | Yes | - | The input image to be modified |
| `prompt` | STRING | Yes | - | Prompt for the image generation (default: "") |
| `n` | INT | Yes | 1-6 | The number of images to generate (default: 1) |
| `strength` | FLOAT | Yes | 0.0-1.0 | Defines the difference with the original image, should lie in [0, 1], where 0 means almost identical, and 1 means miserable similarity (default: 0.5) |
| `seed` | INT | Yes | 0-18446744073709551615 | Seed to determine if node should re-run; actual results are nondeterministic regardless of seed (default: 0) |
| `recraft_style` | STYLEV3 | No | - | Optional style selection for the image generation |
| `negative_prompt` | STRING | No | - | An optional text description of undesired elements on an image (default: "") |
| `recraft_controls` | CONTROLS | No | - | Optional additional controls over the generation via the Recraft Controls node |

**Note:** The `seed` parameter only triggers re-execution of the node but does not guarantee deterministic results. The strength parameter is rounded to 2 decimal places internally.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `image` | IMAGE | The generated image(s) based on the input image and prompt |
