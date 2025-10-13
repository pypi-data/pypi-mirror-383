> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SkipLayerGuidanceSD3/en.md)

The SkipLayerGuidanceSD3 node enhances guidance towards detailed structure by applying an additional set of classifier-free guidance with skipped layers. This experimental implementation is inspired by Perturbed Attention Guidance and works by selectively bypassing certain layers during the negative conditioning process to improve structural details in the generated output.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model to apply skip layer guidance to |
| `layers` | STRING | Yes | - | Comma-separated list of layer indices to skip (default: "7, 8, 9") |
| `scale` | FLOAT | Yes | 0.0 - 10.0 | The strength of the skip layer guidance effect (default: 3.0) |
| `start_percent` | FLOAT | Yes | 0.0 - 1.0 | The starting point of guidance application as a percentage of total steps (default: 0.01) |
| `end_percent` | FLOAT | Yes | 0.0 - 1.0 | The ending point of guidance application as a percentage of total steps (default: 0.15) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with skip layer guidance applied |
