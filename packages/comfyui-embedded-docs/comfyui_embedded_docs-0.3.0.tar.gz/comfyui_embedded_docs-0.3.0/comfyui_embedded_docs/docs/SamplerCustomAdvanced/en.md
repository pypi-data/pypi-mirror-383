> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SamplerCustomAdvanced/en.md)

The SamplerCustomAdvanced node performs advanced latent space sampling using custom noise, guidance, and sampling configurations. It processes a latent image through a guided sampling process with customizable noise generation and sigma schedules, producing both the final sampled output and a denoised version when available.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `noise` | NOISE | Yes | - | The noise generator that provides the initial noise pattern and seed for the sampling process |
| `guider` | GUIDER | Yes | - | The guidance model that directs the sampling process toward desired outputs |
| `sampler` | SAMPLER | Yes | - | The sampling algorithm that defines how the latent space is traversed during generation |
| `sigmas` | SIGMAS | Yes | - | The sigma schedule that controls the noise levels throughout the sampling steps |
| `latent_image` | LATENT | Yes | - | The initial latent representation that serves as the starting point for sampling |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | LATENT | The final sampled latent representation after completing the sampling process |
| `denoised_output` | LATENT | A denoised version of the output when available, otherwise returns the same as the output |
