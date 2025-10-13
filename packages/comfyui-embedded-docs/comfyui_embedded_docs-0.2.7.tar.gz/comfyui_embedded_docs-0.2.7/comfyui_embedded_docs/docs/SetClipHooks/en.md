> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SetClipHooks/en.md)

The SetClipHooks node allows you to apply custom hooks to a CLIP model, enabling advanced modifications to its behavior. It can apply hooks to conditioning outputs and optionally enable clip scheduling functionality. This node creates a cloned copy of the input CLIP model with the specified hook configurations applied.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `clip` | CLIP | Yes | - | The CLIP model to apply hooks to |
| `apply_to_conds` | BOOLEAN | Yes | - | Whether to apply hooks to conditioning outputs (default: True) |
| `schedule_clip` | BOOLEAN | Yes | - | Whether to enable clip scheduling (default: False) |
| `hooks` | HOOKS | No | - | Optional hook group to apply to the CLIP model |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `clip` | CLIP | A cloned CLIP model with the specified hooks applied |
