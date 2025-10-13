> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SamplerDPMPP_2S_Ancestral/en.md)

The SamplerDPMPP_2S_Ancestral node creates a sampler that uses the DPM++ 2S Ancestral sampling method for generating images. This sampler combines deterministic and stochastic elements to produce varied results while maintaining some consistency. It allows you to control the randomness and noise levels during the sampling process.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `eta` | FLOAT | Yes | 0.0 - 100.0 | Controls the amount of stochastic noise added during sampling (default: 1.0) |
| `s_noise` | FLOAT | Yes | 0.0 - 100.0 | Controls the scale of noise applied during the sampling process (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `sampler` | SAMPLER | Returns a configured sampler object that can be used in the sampling pipeline |
