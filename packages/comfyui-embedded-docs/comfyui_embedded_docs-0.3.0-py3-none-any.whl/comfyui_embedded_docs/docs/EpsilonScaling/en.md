> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](<https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/Epsilon> Scaling/en.md)

Implements the Epsilon Scaling method from the research paper "Elucidating the Exposure Bias in Diffusion Models." This method improves sample quality by scaling the predicted noise during the sampling process. It uses a uniform schedule to mitigate exposure bias in diffusion models.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model to apply epsilon scaling to |
| `scaling_factor` | FLOAT | No | 0.5 - 1.5 | The factor used to scale the predicted noise (default: 1.005) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The model with epsilon scaling applied |
