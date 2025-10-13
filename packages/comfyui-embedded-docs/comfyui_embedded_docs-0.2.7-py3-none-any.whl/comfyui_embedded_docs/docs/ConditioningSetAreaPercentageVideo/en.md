> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ConditioningSetAreaPercentageVideo/en.md)

The ConditioningSetAreaPercentageVideo node modifies conditioning data by defining a specific area and temporal region for video generation. It allows you to set the position, size, and duration of the area where the conditioning will be applied using percentage values relative to the overall dimensions. This is useful for focusing the generation on specific parts of a video sequence.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `conditioning` | CONDITIONING | Required | - | - | The conditioning data to be modified |
| `width` | FLOAT | Required | 1.0 | 0.0 - 1.0 | The width of the area as a percentage of the total width |
| `height` | FLOAT | Required | 1.0 | 0.0 - 1.0 | The height of the area as a percentage of the total height |
| `temporal` | FLOAT | Required | 1.0 | 0.0 - 1.0 | The temporal duration of the area as a percentage of the total video length |
| `x` | FLOAT | Required | 0.0 | 0.0 - 1.0 | The horizontal starting position of the area as a percentage |
| `y` | FLOAT | Required | 0.0 | 0.0 - 1.0 | The vertical starting position of the area as a percentage |
| `z` | FLOAT | Required | 0.0 | 0.0 - 1.0 | The temporal starting position of the area as a percentage of the video timeline |
| `strength` | FLOAT | Required | 1.0 | 0.0 - 10.0 | The strength multiplier applied to the conditioning within the defined area |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `conditioning` | CONDITIONING | The modified conditioning data with the specified area and strength settings applied |
