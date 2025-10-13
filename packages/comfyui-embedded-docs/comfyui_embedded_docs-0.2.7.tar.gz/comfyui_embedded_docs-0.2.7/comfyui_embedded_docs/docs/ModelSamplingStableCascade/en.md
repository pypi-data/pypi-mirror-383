> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelSamplingStableCascade/en.md)

The ModelSamplingStableCascade node applies stable cascade sampling to a model by adjusting the sampling parameters with a shift value. It creates a modified version of the input model with custom sampling configuration for stable cascade generation.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The input model to apply stable cascade sampling to |
| `shift` | FLOAT | Yes | 0.0 - 100.0 | The shift value to apply to the sampling parameters (default: 2.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with stable cascade sampling applied |
