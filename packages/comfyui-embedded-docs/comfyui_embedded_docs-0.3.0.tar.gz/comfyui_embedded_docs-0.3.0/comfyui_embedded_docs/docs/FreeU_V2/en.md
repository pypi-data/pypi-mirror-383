> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/FreeU_V2/en.md)

The FreeU_V2 node applies a frequency-based enhancement to diffusion models by modifying the U-Net architecture. It scales different feature channels using configurable parameters to improve image generation quality without requiring additional training. The node works by patching the model's output blocks to apply scaling factors to specific channel dimensions.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The diffusion model to apply FreeU enhancement to |
| `b1` | FLOAT | Yes | 0.0 - 10.0 | Backbone feature scaling factor for the first block (default: 1.3) |
| `b2` | FLOAT | Yes | 0.0 - 10.0 | Backbone feature scaling factor for the second block (default: 1.4) |
| `s1` | FLOAT | Yes | 0.0 - 10.0 | Skip feature scaling factor for the first block (default: 0.9) |
| `s2` | FLOAT | Yes | 0.0 - 10.0 | Skip feature scaling factor for the second block (default: 0.2) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The enhanced diffusion model with FreeU modifications applied |
