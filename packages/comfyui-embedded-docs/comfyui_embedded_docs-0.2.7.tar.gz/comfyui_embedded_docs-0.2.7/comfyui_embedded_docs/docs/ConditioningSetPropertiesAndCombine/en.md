> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ConditioningSetPropertiesAndCombine/en.md)

The ConditioningSetPropertiesAndCombine node modifies conditioning data by applying properties from a new conditioning input to an existing conditioning input. It combines the two conditioning sets while controlling the strength of the new conditioning and specifying how the conditioning area should be applied.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `cond` | CONDITIONING | Required | - | - | The original conditioning data to be modified |
| `cond_NEW` | CONDITIONING | Required | - | - | The new conditioning data providing properties to apply |
| `strength` | FLOAT | Required | 1.0 | 0.0 - 10.0 | Controls the intensity of the new conditioning properties |
| `set_cond_area` | STRING | Required | default | ["default", "mask bounds"] | Determines how the conditioning area is applied |
| `mask` | MASK | Optional | - | - | Optional mask to define specific areas for conditioning |
| `hooks` | HOOKS | Optional | - | - | Optional hook functions for custom processing |
| `timesteps` | TIMESTEPS_RANGE | Optional | - | - | Optional timestep range for controlling when conditioning is applied |

**Note:** When `mask` is provided, the `set_cond_area` parameter can use "mask bounds" to constrain the conditioning application to the masked regions.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `CONDITIONING` | CONDITIONING | The combined conditioning data with modified properties |
