> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CombineHooksEight/en.md)

The Combine Hooks [8] node merges up to eight different hook groups into a single combined hook group. It takes multiple hook inputs and combines them using ComfyUI's hook combination functionality. This allows you to consolidate multiple hook configurations for streamlined processing in advanced workflows.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `hooks_A` | HOOKS | optional | None | - | First hook group to combine |
| `hooks_B` | HOOKS | optional | None | - | Second hook group to combine |
| `hooks_C` | HOOKS | optional | None | - | Third hook group to combine |
| `hooks_D` | HOOKS | optional | None | - | Fourth hook group to combine |
| `hooks_E` | HOOKS | optional | None | - | Fifth hook group to combine |
| `hooks_F` | HOOKS | optional | None | - | Sixth hook group to combine |
| `hooks_G` | HOOKS | optional | None | - | Seventh hook group to combine |
| `hooks_H` | HOOKS | optional | None | - | Eighth hook group to combine |

**Note:** All input parameters are optional. The node will combine only the hook groups that are provided, ignoring any that are left empty. You can provide anywhere from one to eight hook groups for combination.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `HOOKS` | HOOKS | A single combined hook group containing all the provided hook configurations |
