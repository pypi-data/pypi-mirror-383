> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SamplerDPMPP_SDE/en.md)

The SamplerDPMPP_SDE node creates a DPM++ SDE (Stochastic Differential Equation) sampler for use in the sampling process. This sampler provides a stochastic sampling method with configurable noise parameters and device selection. It returns a sampler object that can be used in the sampling pipeline.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `eta` | FLOAT | Yes | 0.0 - 100.0 | Controls the stochasticity of the sampling process (default: 1.0) |
| `s_noise` | FLOAT | Yes | 0.0 - 100.0 | Controls the amount of noise added during sampling (default: 1.0) |
| `r` | FLOAT | Yes | 0.0 - 100.0 | A parameter that influences the sampling behavior (default: 0.5) |
| `noise_device` | COMBO | Yes | "gpu"<br>"cpu" | Selects the device where noise calculations are performed |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `sampler` | SAMPLER | Returns a configured DPM++ SDE sampler object for use in sampling pipelines |
