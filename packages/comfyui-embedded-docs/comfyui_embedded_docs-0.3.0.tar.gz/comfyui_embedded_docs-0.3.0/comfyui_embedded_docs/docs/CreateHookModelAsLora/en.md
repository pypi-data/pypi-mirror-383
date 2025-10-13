> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CreateHookModelAsLora/en.md)

This node creates a hook model as a LoRA (Low-Rank Adaptation) by loading checkpoint weights and applying strength adjustments to both the model and CLIP components. It allows you to apply LoRA-style modifications to existing models through a hook-based approach, enabling fine-tuning and adaptation without permanent model changes. The node can combine with previous hooks and caches loaded weights for efficiency.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `ckpt_name` | COMBO | Yes | Multiple options available | The checkpoint file to load weights from (select from available checkpoints) |
| `strength_model` | FLOAT | Yes | -20.0 to 20.0 | The strength multiplier applied to the model weights (default: 1.0) |
| `strength_clip` | FLOAT | Yes | -20.0 to 20.0 | The strength multiplier applied to the CLIP weights (default: 1.0) |
| `prev_hooks` | HOOKS | No | - | Optional previous hooks to combine with the newly created LoRA hooks |

**Parameter Constraints:**

- The `ckpt_name` parameter loads checkpoints from the available checkpoints folder
- Both strength parameters accept values from -20.0 to 20.0 with 0.01 step increments
- When `prev_hooks` is not provided, the node creates a new hook group
- The node caches loaded weights to avoid reloading the same checkpoint multiple times

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `HOOKS` | HOOKS | The created LoRA hooks, combined with any previous hooks if provided |
