> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelSamplingAuraFlow/en.md)

The ModelSamplingAuraFlow node applies a specialized sampling configuration to diffusion models, specifically designed for AuraFlow model architectures. It modifies the model's sampling behavior by applying a shift parameter that adjusts the sampling distribution. This node inherits from the SD3 model sampling framework and provides fine control over the sampling process.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The diffusion model to apply the AuraFlow sampling configuration to |
| `shift` | FLOAT | Yes | 0.0 - 100.0 | The shift value to apply to the sampling distribution (default: 1.73) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with AuraFlow sampling configuration applied |
