> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LTXVScheduler/en.md)

The LTXVScheduler node generates sigma values for custom sampling processes. It calculates noise schedule parameters based on the number of tokens in the input latent and applies a sigmoid transformation to create the sampling schedule. The node can optionally stretch the resulting sigmas to match a specified terminal value.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `steps` | INT | Yes | 1-10000 | Number of sampling steps (default: 20) |
| `max_shift` | FLOAT | Yes | 0.0-100.0 | Maximum shift value for sigma calculation (default: 2.05) |
| `base_shift` | FLOAT | Yes | 0.0-100.0 | Base shift value for sigma calculation (default: 0.95) |
| `stretch` | BOOLEAN | Yes | True/False | Stretch the sigmas to be in the range [terminal, 1] (default: True) |
| `terminal` | FLOAT | Yes | 0.0-0.99 | The terminal value of the sigmas after stretching (default: 0.1) |
| `latent` | LATENT | No | - | Optional latent input used to calculate token count for sigma adjustment |

**Note:** The `latent` parameter is optional. When not provided, the node uses a default token count of 4096 for calculations.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `sigmas` | SIGMAS | Generated sigma values for the sampling process |
