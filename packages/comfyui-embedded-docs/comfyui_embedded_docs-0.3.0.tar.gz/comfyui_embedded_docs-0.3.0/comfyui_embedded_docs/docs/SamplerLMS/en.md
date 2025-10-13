> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SamplerLMS/en.md)

The SamplerLMS node creates a Least Mean Squares (LMS) sampler for use in diffusion models. It generates a sampler object that can be used in the sampling process, allowing you to control the order of the LMS algorithm for numerical stability and accuracy.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `order` | INT | Yes | 1 to 100 | The order parameter for the LMS sampler algorithm, which controls the numerical method's accuracy and stability (default: 4) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `sampler` | SAMPLER | A configured LMS sampler object that can be used in the sampling pipeline |
