> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/GITSScheduler/en.md)

The GITSScheduler node generates noise schedule sigmas for the GITS (Generative Iterative Time Steps) sampling method. It calculates sigma values based on a coefficient parameter and number of steps, with an optional denoising factor that can reduce the total steps used. The node uses pre-defined noise levels and interpolation to create the final sigma schedule.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `coeff` | FLOAT | Yes | 0.80 - 1.50 | The coefficient value that controls the noise schedule curve (default: 1.20) |
| `steps` | INT | Yes | 2 - 1000 | The total number of sampling steps to generate sigmas for (default: 10) |
| `denoise` | FLOAT | Yes | 0.0 - 1.0 | Denoising factor that reduces the number of steps used (default: 1.0) |

**Note:** When `denoise` is set to 0.0, the node returns an empty tensor. When `denoise` is less than 1.0, the actual number of steps used is calculated as `round(steps * denoise)`.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `sigmas` | SIGMAS | The generated sigma values for the noise schedule |
