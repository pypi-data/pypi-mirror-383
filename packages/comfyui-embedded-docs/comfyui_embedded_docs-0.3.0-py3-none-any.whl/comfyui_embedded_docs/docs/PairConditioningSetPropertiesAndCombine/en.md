> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PairConditioningSetPropertiesAndCombine/en.md)

The PairConditioningSetPropertiesAndCombine node modifies and combines conditioning pairs by applying new conditioning data to existing positive and negative conditioning inputs. It allows you to adjust the strength of the applied conditioning and control how the conditioning area is set. This node is particularly useful for advanced conditioning manipulation workflows where you need to blend multiple conditioning sources together.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | The original positive conditioning input |
| `negative` | CONDITIONING | Yes | - | The original negative conditioning input |
| `positive_NEW` | CONDITIONING | Yes | - | The new positive conditioning to apply |
| `negative_NEW` | CONDITIONING | Yes | - | The new negative conditioning to apply |
| `strength` | FLOAT | Yes | 0.0 to 10.0 | The strength factor for applying the new conditioning (default: 1.0) |
| `set_cond_area` | STRING | Yes | "default"<br>"mask bounds" | Controls how the conditioning area is applied |
| `mask` | MASK | No | - | Optional mask to constrain the conditioning application area |
| `hooks` | HOOKS | No | - | Optional hook group for advanced control |
| `timesteps` | TIMESTEPS_RANGE | No | - | Optional timestep range specification |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | The combined positive conditioning output |
| `negative` | CONDITIONING | The combined negative conditioning output |
