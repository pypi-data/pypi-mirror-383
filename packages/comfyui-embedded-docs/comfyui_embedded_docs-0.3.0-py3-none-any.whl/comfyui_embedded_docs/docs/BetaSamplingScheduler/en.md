> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/BetaSamplingScheduler/en.md)

The BetaSamplingScheduler node generates a sequence of noise levels (sigmas) for the sampling process using a beta scheduling algorithm. It takes a model and configuration parameters to create a customized noise schedule that controls the denoising process during image generation. This scheduler allows fine-tuning of the noise reduction trajectory through alpha and beta parameters.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `model` | MODEL | Required | - | - | The model used for sampling, which provides the model sampling object |
| `steps` | INT | Required | 20 | 1-10000 | The number of sampling steps to generate sigmas for |
| `alpha` | FLOAT | Required | 0.6 | 0.0-50.0 | Alpha parameter for the beta scheduler, controlling the scheduling curve |
| `beta` | FLOAT | Required | 0.6 | 0.0-50.0 | Beta parameter for the beta scheduler, controlling the scheduling curve |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `SIGMAS` | SIGMAS | A sequence of noise levels (sigmas) used for the sampling process |
