> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SamplerDPMPP_3M_SDE/en.md)

The SamplerDPMPP_3M_SDE node creates a DPM++ 3M SDE sampler for use in the sampling process. This sampler uses a third-order multistep stochastic differential equation method with configurable noise parameters. The node allows you to choose whether noise calculations are performed on the GPU or CPU.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `eta` | FLOAT | Yes | 0.0 - 100.0 | Controls the stochasticity of the sampling process (default: 1.0) |
| `s_noise` | FLOAT | Yes | 0.0 - 100.0 | Controls the amount of noise added during sampling (default: 1.0) |
| `noise_device` | COMBO | Yes | "gpu"<br>"cpu" | Selects the device for noise calculations, either GPU or CPU |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `sampler` | SAMPLER | Returns a configured sampler object for use in sampling workflows |
