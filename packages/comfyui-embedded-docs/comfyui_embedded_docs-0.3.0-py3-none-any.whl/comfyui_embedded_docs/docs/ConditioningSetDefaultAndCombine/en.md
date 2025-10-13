> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ConditioningSetDefaultAndCombine/en.md)

This node combines conditioning data with default conditioning data using a hook-based system. It takes a primary conditioning input and a default conditioning input, then merges them according to the specified hook configuration. The result is a single conditioning output that incorporates both sources.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `cond` | CONDITIONING | Required | - | - | The primary conditioning input to be processed |
| `cond_DEFAULT` | CONDITIONING | Required | - | - | The default conditioning data to be combined with the primary conditioning |
| `hooks` | HOOKS | Optional | - | - | Optional hook configuration that controls how the conditioning data is processed and combined |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `CONDITIONING` | CONDITIONING | The combined conditioning data resulting from merging the primary and default conditioning inputs |
