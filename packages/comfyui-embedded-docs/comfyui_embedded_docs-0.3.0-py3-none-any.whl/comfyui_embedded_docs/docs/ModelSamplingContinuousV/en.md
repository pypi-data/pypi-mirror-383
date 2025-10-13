> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelSamplingContinuousV/en.md)

The ModelSamplingContinuousV node modifies a model's sampling behavior by applying continuous V-prediction sampling parameters. It creates a clone of the input model and configures it with custom sigma range settings for advanced sampling control. This allows users to fine-tune the sampling process with specific minimum and maximum sigma values.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The input model to be modified with continuous V-prediction sampling |
| `sampling` | STRING | Yes | "v_prediction" | The sampling method to apply (currently only V-prediction is supported) |
| `sigma_max` | FLOAT | Yes | 0.0 - 1000.0 | The maximum sigma value for sampling (default: 500.0) |
| `sigma_min` | FLOAT | Yes | 0.0 - 1000.0 | The minimum sigma value for sampling (default: 0.03) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with continuous V-prediction sampling applied |
