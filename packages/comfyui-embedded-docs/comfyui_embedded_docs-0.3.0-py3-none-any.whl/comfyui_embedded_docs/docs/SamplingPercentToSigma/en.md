> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SamplingPercentToSigma/en.md)

The SamplingPercentToSigma node converts a sampling percentage value to a corresponding sigma value using the model's sampling parameters. It takes a percentage value between 0.0 and 1.0 and maps it to the appropriate sigma value in the model's noise schedule, with options to return either the calculated sigma or the actual maximum/minimum sigma values at the boundaries.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model containing the sampling parameters used for conversion |
| `sampling_percent` | FLOAT | Yes | 0.0 to 1.0 | The sampling percentage to convert to sigma (default: 0.0) |
| `return_actual_sigma` | BOOLEAN | Yes | - | Return the actual sigma value instead of the value used for interval checks. This only affects results at 0.0 and 1.0. (default: False) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `sigma_value` | FLOAT | The converted sigma value corresponding to the input sampling percentage |
