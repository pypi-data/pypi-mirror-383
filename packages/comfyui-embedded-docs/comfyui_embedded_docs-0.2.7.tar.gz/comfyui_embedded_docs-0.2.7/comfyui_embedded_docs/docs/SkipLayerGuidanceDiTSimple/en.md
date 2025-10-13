> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SkipLayerGuidanceDiTSimple/en.md)

Simple version of the SkipLayerGuidanceDiT node that only modifies the unconditional pass during the denoising process. This node applies skip layer guidance to specific transformer layers in DiT (Diffusion Transformer) models by selectively skipping certain layers during the unconditional pass based on specified timing and layer parameters.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model to apply skip layer guidance to |
| `double_layers` | STRING | Yes | - | Comma-separated list of double block layer indices to skip (default: "7, 8, 9") |
| `single_layers` | STRING | Yes | - | Comma-separated list of single block layer indices to skip (default: "7, 8, 9") |
| `start_percent` | FLOAT | Yes | 0.0 - 1.0 | The starting percentage of the denoising process when skip layer guidance begins (default: 0.0) |
| `end_percent` | FLOAT | Yes | 0.0 - 1.0 | The ending percentage of the denoising process when skip layer guidance stops (default: 1.0) |

**Note:** Skip layer guidance is only applied when both `double_layers` and `single_layers` contain valid layer indices. If both are empty, the node returns the original model unchanged.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with skip layer guidance applied to the specified layers |
