> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SamplerDPMAdaptative/en.md)

The SamplerDPMAdaptative node implements an adaptive DPM (Diffusion Probabilistic Model) sampler that automatically adjusts step sizes during the sampling process. It uses tolerance-based error control to determine optimal step sizes, balancing computational efficiency with sampling accuracy. This adaptive approach helps maintain quality while potentially reducing the number of steps needed.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `order` | INT | Yes | 2-3 | The order of the sampler method (default: 3) |
| `rtol` | FLOAT | Yes | 0.0-100.0 | Relative tolerance for error control (default: 0.05) |
| `atol` | FLOAT | Yes | 0.0-100.0 | Absolute tolerance for error control (default: 0.0078) |
| `h_init` | FLOAT | Yes | 0.0-100.0 | Initial step size (default: 0.05) |
| `pcoeff` | FLOAT | Yes | 0.0-100.0 | Proportional coefficient for step size control (default: 0.0) |
| `icoeff` | FLOAT | Yes | 0.0-100.0 | Integral coefficient for step size control (default: 1.0) |
| `dcoeff` | FLOAT | Yes | 0.0-100.0 | Derivative coefficient for step size control (default: 0.0) |
| `accept_safety` | FLOAT | Yes | 0.0-100.0 | Safety factor for step acceptance (default: 0.81) |
| `eta` | FLOAT | Yes | 0.0-100.0 | Stochasticity parameter (default: 0.0) |
| `s_noise` | FLOAT | Yes | 0.0-100.0 | Noise scaling factor (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `sampler` | SAMPLER | Returns a configured DPM adaptive sampler instance |
