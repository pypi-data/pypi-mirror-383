> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SplitSigmasDenoise/en.md)

The SplitSigmasDenoise node divides a sequence of sigma values into two parts based on a denoising strength parameter. It splits the input sigmas into high and low sigma sequences, where the split point is determined by multiplying the total steps by the denoise factor. This allows for separating the noise schedule into different intensity ranges for specialized processing.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `sigmas` | SIGMAS | Yes | - | The input sequence of sigma values representing the noise schedule |
| `denoise` | FLOAT | Yes | 0.0 - 1.0 | The denoising strength factor that determines where to split the sigma sequence (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `high_sigmas` | SIGMAS | The first portion of the sigma sequence containing higher sigma values |
| `low_sigmas` | SIGMAS | The second portion of the sigma sequence containing lower sigma values |
