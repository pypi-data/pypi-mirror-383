> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ConditioningSetProperties/en.md)

The ConditioningSetProperties node modifies the properties of conditioning data by adjusting strength, area settings, and applying optional masks or timestep ranges. It allows you to control how conditioning influences the generation process by setting specific parameters that affect the application of conditioning data during image generation.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `cond_NEW` | CONDITIONING | Required | - | - | The conditioning data to modify |
| `strength` | FLOAT | Required | 1.0 | 0.0-10.0 | Controls the intensity of the conditioning effect |
| `set_cond_area` | STRING | Required | default | ["default", "mask bounds"] | Determines how the conditioning area is applied |
| `mask` | MASK | Optional | - | - | Optional mask to restrict where conditioning is applied |
| `hooks` | HOOKS | Optional | - | - | Optional hook functions for custom processing |
| `timesteps` | TIMESTEPS_RANGE | Optional | - | - | Optional timestep range to limit when conditioning is active |

**Note:** When a `mask` is provided, the `set_cond_area` parameter can be set to "mask bounds" to restrict conditioning application to the masked region only.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `CONDITIONING` | CONDITIONING | The modified conditioning data with updated properties |
