> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SetFirstSigma/en.md)

The SetFirstSigma node modifies a sequence of sigma values by replacing the first sigma value in the sequence with a custom value. It takes an existing sigma sequence and a new sigma value as inputs, then returns a new sigma sequence where only the first element has been changed while keeping all other sigma values unchanged.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `sigmas` | SIGMAS | Yes | - | The input sequence of sigma values to be modified |
| `sigma` | FLOAT | Yes | 0.0 to 20000.0 | The new sigma value to set as the first element in the sequence (default: 136.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `sigmas` | SIGMAS | The modified sigma sequence with the first element replaced by the custom sigma value |
