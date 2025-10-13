> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SamplerEulerAncestralCFGPP/en.md)

The SamplerEulerAncestralCFGPP node creates a specialized sampler for generating images using the Euler Ancestral method with classifier-free guidance. This sampler combines ancestral sampling techniques with guidance conditioning to produce diverse image variations while maintaining coherence. It allows fine-tuning of the sampling process through parameters that control noise and step size adjustments.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `eta` | FLOAT | Yes | 0.0 - 1.0 | Controls the step size during sampling, with higher values resulting in more aggressive updates (default: 1.0) |
| `s_noise` | FLOAT | Yes | 0.0 - 10.0 | Adjusts the amount of noise added during the sampling process (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `sampler` | SAMPLER | Returns a configured sampler object that can be used in the image generation pipeline |
