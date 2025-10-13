> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CreateHookLora/en.md)

The Create Hook LoRA node generates hook objects for applying LoRA (Low-Rank Adaptation) modifications to models. It loads a specified LoRA file and creates hooks that can adjust model and CLIP strengths, then combines these hooks with any existing hooks passed to it. The node efficiently manages LoRA loading by caching previously loaded LoRA files to avoid redundant operations.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `lora_name` | STRING | Yes | Multiple options available | The name of the LoRA file to load from the loras directory |
| `strength_model` | FLOAT | Yes | -20.0 to 20.0 | The strength multiplier for model adjustments (default: 1.0) |
| `strength_clip` | FLOAT | Yes | -20.0 to 20.0 | The strength multiplier for CLIP adjustments (default: 1.0) |
| `prev_hooks` | HOOKS | No | N/A | Optional existing hook group to combine with the new LoRA hooks |

**Parameter Constraints:**

- If both `strength_model` and `strength_clip` are set to 0, the node will skip creating new LoRA hooks and return the existing hooks unchanged
- The node caches the last loaded LoRA file to optimize performance when the same LoRA is used repeatedly

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `HOOKS` | HOOKS | A hook group containing the combined LoRA hooks and any previous hooks |
