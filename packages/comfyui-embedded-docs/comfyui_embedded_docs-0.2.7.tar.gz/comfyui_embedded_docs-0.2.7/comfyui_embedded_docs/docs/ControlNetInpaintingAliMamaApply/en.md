> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ControlNetInpaintingAliMamaApply/en.md)

The ControlNetInpaintingAliMamaApply node applies ControlNet conditioning for inpainting tasks by combining positive and negative conditioning with a control image and mask. It processes the input image and mask to create modified conditioning that guides the generation process, allowing for precise control over which areas of the image are inpainted. The node supports strength adjustment and timing controls to fine-tune the ControlNet's influence during different stages of the generation process.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | The positive conditioning that guides the generation toward desired content |
| `negative` | CONDITIONING | Yes | - | The negative conditioning that guides the generation away from unwanted content |
| `control_net` | CONTROL_NET | Yes | - | The ControlNet model that provides additional control over the generation |
| `vae` | VAE | Yes | - | The VAE (Variational Autoencoder) used for encoding and decoding images |
| `image` | IMAGE | Yes | - | The input image that serves as control guidance for the ControlNet |
| `mask` | MASK | Yes | - | The mask that defines which areas of the image should be inpainted |
| `strength` | FLOAT | Yes | 0.0 to 10.0 | The strength of the ControlNet effect (default: 1.0) |
| `start_percent` | FLOAT | Yes | 0.0 to 1.0 | The starting point (as percentage) of when ControlNet influence begins during generation (default: 0.0) |
| `end_percent` | FLOAT | Yes | 0.0 to 1.0 | The ending point (as percentage) of when ControlNet influence stops during generation (default: 1.0) |

**Note:** When the ControlNet has `concat_mask` enabled, the mask is inverted and applied to the image before processing, and the mask is included in the extra concatenation data sent to the ControlNet.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | The modified positive conditioning with ControlNet applied for inpainting |
| `negative` | CONDITIONING | The modified negative conditioning with ControlNet applied for inpainting |
