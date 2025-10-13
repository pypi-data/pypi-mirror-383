> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LatentOperationTonemapReinhard/en.md)

The LatentOperationTonemapReinhard node applies Reinhard tonemapping to latent vectors. This technique normalizes the latent vectors and adjusts their magnitude using a statistical approach based on mean and standard deviation, with the intensity controlled by a multiplier parameter.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `multiplier` | FLOAT | No | 0.0 to 100.0 | Controls the intensity of the tonemapping effect (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `operation` | LATENT_OPERATION | Returns a tonemapping operation that can be applied to latent vectors |
