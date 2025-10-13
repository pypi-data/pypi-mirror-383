> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/AddNoise/en.md)

# AddNoise

This node adds controlled noise to a latent image using specified noise parameters and sigma values. It processes the input through the model's sampling system to apply noise scaling appropriate for the given sigma range.

## How It Works

The node takes a latent image and applies noise to it based on the provided noise generator and sigma values. It first checks if there are any sigmas provided - if not, it returns the original latent image unchanged. The node then uses the model's sampling system to process the latent image and apply scaled noise. The noise scaling is determined by the difference between the first and last sigma values when multiple sigmas are provided, or by the single sigma value when only one is available. Empty latent images (containing only zeros) are not shifted during processing. The final output is a new latent representation with the applied noise, with any NaN or infinite values converted to zeros for stability.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `model` | MODEL | Required | - | - | The model containing sampling parameters and processing functions |
| `noise` | NOISE | Required | - | - | The noise generator that produces the base noise pattern |
| `sigmas` | SIGMAS | Required | - | - | Sigma values controlling the noise scaling intensity |
| `latent_image` | LATENT | Required | - | - | The input latent representation to which noise will be added |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `LATENT` | LATENT | The modified latent representation with added noise |
