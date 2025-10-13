> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SkipLayerGuidanceDiT/en.md)

Enhances guidance towards detailed structure by using another set of CFG negative with skipped layers. This generic version of SkipLayerGuidance can be used on every DiT model and is inspired by Perturbed Attention Guidance. The original experimental implementation was created for SD3.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model to apply skip layer guidance to |
| `double_layers` | STRING | Yes | - | Comma-separated layer numbers for double blocks to skip (default: "7, 8, 9") |
| `single_layers` | STRING | Yes | - | Comma-separated layer numbers for single blocks to skip (default: "7, 8, 9") |
| `scale` | FLOAT | Yes | 0.0 - 10.0 | Guidance scale factor (default: 3.0) |
| `start_percent` | FLOAT | Yes | 0.0 - 1.0 | Starting percentage for guidance application (default: 0.01) |
| `end_percent` | FLOAT | Yes | 0.0 - 1.0 | Ending percentage for guidance application (default: 0.15) |
| `rescaling_scale` | FLOAT | Yes | 0.0 - 10.0 | Rescaling scale factor (default: 0.0) |

**Note:** If both `double_layers` and `single_layers` are empty (contain no layer numbers), the node returns the original model without applying any guidance.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with skip layer guidance applied |
