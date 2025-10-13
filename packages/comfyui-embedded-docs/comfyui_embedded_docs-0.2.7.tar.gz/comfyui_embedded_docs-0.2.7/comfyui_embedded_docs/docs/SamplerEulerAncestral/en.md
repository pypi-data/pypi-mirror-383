> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SamplerEulerAncestral/en.md)

The SamplerEulerAncestral node creates an Euler Ancestral sampler for generating images. This sampler uses a specific mathematical approach that combines Euler integration with ancestral sampling techniques to produce image variations. The node allows you to configure the sampling behavior by adjusting parameters that control the randomness and step size during the generation process.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `eta` | FLOAT | Yes | 0.0 - 100.0 | Controls the step size and stochasticity of the sampling process (default: 1.0) |
| `s_noise` | FLOAT | Yes | 0.0 - 100.0 | Controls the amount of noise added during sampling (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `sampler` | SAMPLER | Returns a configured Euler Ancestral sampler that can be used in the sampling pipeline |
