> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ConditioningTimestepsRange/en.md)

The ConditioningTimestepsRange node creates three distinct timestep ranges for controlling when conditioning effects are applied during the generation process. It takes start and end percentage values and divides the entire timestep range (0.0 to 1.0) into three segments: the main range between the specified percentages, the range before the start percentage, and the range after the end percentage.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `start_percent` | FLOAT | Yes | 0.0 - 1.0 | The starting percentage of the timestep range (default: 0.0) |
| `end_percent` | FLOAT | Yes | 0.0 - 1.0 | The ending percentage of the timestep range (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `TIMESTEPS_RANGE` | TIMESTEPS_RANGE | The main timestep range defined by start_percent and end_percent |
| `BEFORE_RANGE` | TIMESTEPS_RANGE | The timestep range from 0.0 to start_percent |
| `AFTER_RANGE` | TIMESTEPS_RANGE | The timestep range from end_percent to 1.0 |
