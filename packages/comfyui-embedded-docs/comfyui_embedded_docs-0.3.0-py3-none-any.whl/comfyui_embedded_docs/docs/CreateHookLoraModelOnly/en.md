> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CreateHookLoraModelOnly/en.md)

This node creates a LoRA (Low-Rank Adaptation) hook that applies only to the model component, allowing you to modify model behavior without affecting the CLIP component. It loads a LoRA file and applies it with a specified strength to the model while keeping the CLIP component unchanged. The node can be chained with previous hooks to create complex modification pipelines.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `lora_name` | STRING | Yes | Multiple options available | The name of the LoRA file to load from the loras folder |
| `strength_model` | FLOAT | Yes | -20.0 to 20.0 | The strength multiplier for applying the LoRA to the model component (default: 1.0) |
| `prev_hooks` | HOOKS | No | - | Optional previous hooks to chain with this hook |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `hooks` | HOOKS | The created LoRA hook that can be applied to model processing |
