> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LatentApplyOperation/en.md)

The LatentApplyOperation node applies a specified operation to latent samples. It takes latent data and an operation as inputs, processes the latent samples using the provided operation, and returns the modified latent data. This node allows you to transform or manipulate latent representations in your workflow.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `samples` | LATENT | Yes | - | The latent samples to be processed by the operation |
| `operation` | LATENT_OPERATION | Yes | - | The operation to apply to the latent samples |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | LATENT | The modified latent samples after applying the operation |
