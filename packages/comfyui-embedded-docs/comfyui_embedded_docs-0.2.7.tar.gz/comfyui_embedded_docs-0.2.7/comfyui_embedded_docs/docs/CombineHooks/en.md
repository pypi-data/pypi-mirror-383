> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CombineHooks/en.md)

The Combine Hooks [2] node merges two hook groups into a single combined hook group. It takes two optional hook inputs and combines them using ComfyUI's hook combination functionality. This allows you to consolidate multiple hook configurations for streamlined processing.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `hooks_A` | HOOKS | Optional | None | - | First hook group to combine |
| `hooks_B` | HOOKS | Optional | None | - | Second hook group to combine |

**Note:** Both inputs are optional, but at least one hook group must be provided for the node to function. If only one hook group is provided, it will be returned unchanged.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `hooks` | HOOKS | Combined hook group containing all hooks from both input groups |
