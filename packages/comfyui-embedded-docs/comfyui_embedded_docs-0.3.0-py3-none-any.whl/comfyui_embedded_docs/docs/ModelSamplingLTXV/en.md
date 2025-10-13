> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelSamplingLTXV/en.md)

The ModelSamplingLTXV node applies advanced sampling parameters to a model based on token count. It calculates a shift value using a linear interpolation between base and maximum shift values, with the calculation depending on the number of tokens in the input latent. The node then creates a specialized model sampling configuration and applies it to the input model.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The input model to apply sampling parameters to |
| `max_shift` | FLOAT | No | 0.0 to 100.0 | The maximum shift value used in calculation (default: 2.05) |
| `base_shift` | FLOAT | No | 0.0 to 100.0 | The base shift value used in calculation (default: 0.95) |
| `latent` | LATENT | No | - | Optional latent input used to determine token count for shift calculation |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with applied sampling parameters |
