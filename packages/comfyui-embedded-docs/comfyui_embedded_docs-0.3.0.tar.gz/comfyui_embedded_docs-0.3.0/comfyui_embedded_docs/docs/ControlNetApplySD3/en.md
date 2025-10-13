> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ControlNetApplySD3/en.md)

This node applies ControlNet guidance to Stable Diffusion 3 conditioning. It takes positive and negative conditioning inputs along with a ControlNet model and image, then applies the control guidance with adjustable strength and timing parameters to influence the generation process.

**Note:** This node has been marked as deprecated and may be removed in future versions.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | The positive conditioning to apply ControlNet guidance to |
| `negative` | CONDITIONING | Yes | - | The negative conditioning to apply ControlNet guidance to |
| `control_net` | CONTROL_NET | Yes | - | The ControlNet model to use for guidance |
| `vae` | VAE | Yes | - | The VAE model used in the process |
| `image` | IMAGE | Yes | - | The input image that ControlNet will use as guidance |
| `strength` | FLOAT | Yes | 0.0 - 10.0 | The strength of the ControlNet effect (default: 1.0) |
| `start_percent` | FLOAT | Yes | 0.0 - 1.0 | The starting point in the generation process where ControlNet begins to apply (default: 0.0) |
| `end_percent` | FLOAT | Yes | 0.0 - 1.0 | The ending point in the generation process where ControlNet stops applying (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | The modified positive conditioning with ControlNet guidance applied |
| `negative` | CONDITIONING | The modified negative conditioning with ControlNet guidance applied |
