> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SamplerDPMPP_2M_SDE/en.md)

The SamplerDPMPP_2M_SDE node creates a DPM++ 2M SDE sampler for diffusion models. This sampler uses second-order differential equation solvers with stochastic differential equations to generate samples. It provides different solver types and noise handling options to control the sampling process.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `solver_type` | STRING | Yes | `"midpoint"`<br>`"heun"` | The type of differential equation solver to use for the sampling process |
| `eta` | FLOAT | Yes | 0.0 - 100.0 | Controls the stochasticity of the sampling process (default: 1.0) |
| `s_noise` | FLOAT | Yes | 0.0 - 100.0 | Controls the amount of noise added during sampling (default: 1.0) |
| `noise_device` | STRING | Yes | `"gpu"`<br>`"cpu"` | The device where noise calculations are performed |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `sampler` | SAMPLER | A configured sampler object ready for use in the sampling pipeline |
