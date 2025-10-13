> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LaplaceScheduler/en.md)

The LaplaceScheduler node generates a sequence of sigma values following a Laplace distribution for use in diffusion sampling. It creates a schedule of noise levels that gradually decrease from a maximum to minimum value, using Laplace distribution parameters to control the progression. This scheduler is commonly used in custom sampling workflows to define the noise schedule for diffusion models.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `steps` | INT | Yes | 1 to 10000 | Number of sampling steps in the schedule (default: 20) |
| `sigma_max` | FLOAT | Yes | 0.0 to 5000.0 | Maximum sigma value at the start of the schedule (default: 14.614642) |
| `sigma_min` | FLOAT | Yes | 0.0 to 5000.0 | Minimum sigma value at the end of the schedule (default: 0.0291675) |
| `mu` | FLOAT | Yes | -10.0 to 10.0 | Mean parameter for the Laplace distribution (default: 0.0) |
| `beta` | FLOAT | Yes | 0.0 to 10.0 | Scale parameter for the Laplace distribution (default: 0.5) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `SIGMAS` | SIGMAS | A sequence of sigma values following a Laplace distribution schedule |
