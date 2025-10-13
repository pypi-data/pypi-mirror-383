> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SamplerSASolver/en.md)

The SamplerSASolver node implements a custom sampling algorithm for diffusion models. It uses a predictor-corrector approach with configurable order settings and stochastic differential equation (SDE) parameters to generate samples from the input model.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The diffusion model to use for sampling |
| `eta` | FLOAT | Yes | 0.0 - 10.0 | Controls the step size scaling factor (default: 1.0) |
| `sde_start_percent` | FLOAT | Yes | 0.0 - 1.0 | The starting percentage for SDE sampling (default: 0.2) |
| `sde_end_percent` | FLOAT | Yes | 0.0 - 1.0 | The ending percentage for SDE sampling (default: 0.8) |
| `s_noise` | FLOAT | Yes | 0.0 - 100.0 | Controls the amount of noise added during sampling (default: 1.0) |
| `predictor_order` | INT | Yes | 1 - 6 | The order of the predictor component in the solver (default: 3) |
| `corrector_order` | INT | Yes | 0 - 6 | The order of the corrector component in the solver (default: 4) |
| `use_pece` | BOOLEAN | Yes | - | Enables or disables the PECE (Predict-Evaluate-Correct-Evaluate) method |
| `simple_order_2` | BOOLEAN | Yes | - | Enables or disables simplified second-order calculations |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `sampler` | SAMPLER | A configured sampler object that can be used with diffusion models |
