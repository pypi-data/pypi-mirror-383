> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RecraftReplaceBackgroundNode/en.md)

Replace background on image, based on provided prompt. This node uses the Recraft API to generate new backgrounds for your images according to your text description, allowing you to completely transform the background while keeping the main subject intact.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `image` | IMAGE | Yes | - | The input image to process |
| `prompt` | STRING | Yes | - | Prompt for the image generation (default: empty) |
| `n` | INT | Yes | 1-6 | The number of images to generate (default: 1) |
| `seed` | INT | Yes | 0-18446744073709551615 | Seed to determine if node should re-run; actual results are nondeterministic regardless of seed (default: 0) |
| `recraft_style` | STYLEV3 | No | - | Optional style selection for the generated background |
| `negative_prompt` | STRING | No | - | An optional text description of undesired elements on an image (default: empty) |

**Note:** The `seed` parameter controls when the node re-executes but does not guarantee deterministic results due to the nature of the external API.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `IMAGE` | IMAGE | The generated image(s) with replaced background |
