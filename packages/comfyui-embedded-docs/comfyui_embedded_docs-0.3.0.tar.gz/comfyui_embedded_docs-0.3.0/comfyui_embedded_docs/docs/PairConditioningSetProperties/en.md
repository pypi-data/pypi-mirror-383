> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PairConditioningSetProperties/en.md)

The PairConditioningSetProperties node allows you to modify the properties of both positive and negative conditioning pairs simultaneously. It applies strength adjustments, conditioning area settings, and optional masking or timing controls to both conditioning inputs, returning the modified positive and negative conditioning data.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive_NEW` | CONDITIONING | Yes | - | The positive conditioning input to modify |
| `negative_NEW` | CONDITIONING | Yes | - | The negative conditioning input to modify |
| `strength` | FLOAT | Yes | 0.0 to 10.0 | The strength multiplier applied to the conditioning (default: 1.0) |
| `set_cond_area` | STRING | Yes | "default"<br>"mask bounds" | Determines how the conditioning area is calculated |
| `mask` | MASK | No | - | Optional mask to constrain the conditioning area |
| `hooks` | HOOKS | No | - | Optional hook group for advanced conditioning modifications |
| `timesteps` | TIMESTEPS_RANGE | No | - | Optional timestep range to limit when conditioning is applied |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | The modified positive conditioning with applied properties |
| `negative` | CONDITIONING | The modified negative conditioning with applied properties |
