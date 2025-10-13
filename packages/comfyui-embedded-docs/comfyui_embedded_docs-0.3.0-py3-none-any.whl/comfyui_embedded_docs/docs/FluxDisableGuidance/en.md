> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/FluxDisableGuidance/en.md)

This node completely disables the guidance embed functionality for Flux and similar models. It takes conditioning data as input and removes the guidance component by setting it to None, effectively turning off guidance-based conditioning for the generation process.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `conditioning` | CONDITIONING | Yes | - | The conditioning data to process and remove guidance from |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `conditioning` | CONDITIONING | The modified conditioning data with guidance disabled |
