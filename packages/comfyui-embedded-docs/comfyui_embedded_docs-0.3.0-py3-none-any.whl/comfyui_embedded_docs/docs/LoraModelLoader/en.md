> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LoraModelLoader/en.md)

The LoraModelLoader node applies trained LoRA (Low-Rank Adaptation) weights to a diffusion model. It modifies the base model by loading LoRA weights from a trained LoRA model and adjusting their influence strength. This allows you to customize the behavior of diffusion models without retraining them from scratch.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The diffusion model the LoRA will be applied to. |
| `lora` | LORA_MODEL | Yes | - | The LoRA model to apply to the diffusion model. |
| `strength_model` | FLOAT | Yes | -100.0 to 100.0 | How strongly to modify the diffusion model. This value can be negative (default: 1.0). |

**Note:** When `strength_model` is set to 0, the node returns the original model without applying any LoRA modifications.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified diffusion model with LoRA weights applied. |
