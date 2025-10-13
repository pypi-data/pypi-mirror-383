> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/FreSca/en.md)

The FreSca node applies frequency-dependent scaling to guidance during the sampling process. It separates the guidance signal into low-frequency and high-frequency components using Fourier filtering, then applies different scaling factors to each frequency range before recombining them. This allows for more nuanced control over how guidance affects different aspects of the generated output.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model to apply frequency scaling to |
| `scale_low` | FLOAT | No | 0-10 | Scaling factor for low-frequency components (default: 1.0) |
| `scale_high` | FLOAT | No | 0-10 | Scaling factor for high-frequency components (default: 1.25) |
| `freq_cutoff` | INT | No | 1-10000 | Number of frequency indices around center to consider as low-frequency (default: 20) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with frequency-dependent scaling applied to its guidance function |
