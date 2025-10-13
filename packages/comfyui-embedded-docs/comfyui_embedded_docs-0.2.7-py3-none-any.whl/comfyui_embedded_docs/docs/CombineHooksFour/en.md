> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CombineHooksFour/en.md)

The Combine Hooks [4] node merges up to four separate hook groups into a single combined hook group. It takes any combination of the four available hook inputs and combines them using ComfyUI's hook combination system. This allows you to consolidate multiple hook configurations for streamlined processing in advanced workflows.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `hooks_A` | HOOKS | optional | None | - | First hook group to combine |
| `hooks_B` | HOOKS | optional | None | - | Second hook group to combine |
| `hooks_C` | HOOKS | optional | None | - | Third hook group to combine |
| `hooks_D` | HOOKS | optional | None | - | Fourth hook group to combine |

**Note:** All four hook inputs are optional. The node will combine only the hook groups that are provided, and will return an empty hook group if no inputs are connected.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `HOOKS` | HOOKS | Combined hook group containing all provided hook configurations |
