> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CreateHookModelAsLoraModelOnly/en.md)

This node creates a hook that applies a LoRA (Low-Rank Adaptation) model to modify only the model component of a neural network. It loads a checkpoint file and applies it with a specified strength to the model while leaving the CLIP component unchanged. This is an experimental node that extends the functionality of the base CreateHookModelAsLora class.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `ckpt_name` | STRING | Yes | Multiple options available | The checkpoint file to load as a LoRA model. Available options depend on the checkpoints folder contents. |
| `strength_model` | FLOAT | Yes | -20.0 to 20.0 | The strength multiplier for applying the LoRA to the model component (default: 1.0) |
| `prev_hooks` | HOOKS | No | - | Optional previous hooks to chain with this hook |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `hooks` | HOOKS | The created hook group containing the LoRA model modification |
