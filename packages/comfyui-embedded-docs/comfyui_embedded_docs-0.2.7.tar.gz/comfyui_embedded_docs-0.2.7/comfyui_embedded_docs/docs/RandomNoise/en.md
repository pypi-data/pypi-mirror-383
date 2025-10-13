> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RandomNoise/en.md)

The RandomNoise node generates random noise patterns based on a seed value. It creates reproducible noise that can be used for various image processing and generation tasks. The same seed will always produce the same noise pattern, allowing for consistent results across multiple runs.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `noise_seed` | INT | Yes | 0 to 18446744073709551615 | The seed value used to generate the random noise pattern (default: 0). The same seed will always produce the same noise output. |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `noise` | NOISE | The generated random noise pattern based on the provided seed value. |
