> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ConditioningStableAudio/en.md)

The ConditioningStableAudio node adds timing information to both positive and negative conditioning inputs for audio generation. It sets the start time and total duration parameters that help control when and how long audio content should be generated. This node modifies existing conditioning data by appending audio-specific timing metadata.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | The positive conditioning input to be modified with audio timing information |
| `negative` | CONDITIONING | Yes | - | The negative conditioning input to be modified with audio timing information |
| `seconds_start` | FLOAT | Yes | 0.0 to 1000.0 | The starting time in seconds for audio generation (default: 0.0) |
| `seconds_total` | FLOAT | Yes | 0.0 to 1000.0 | The total duration in seconds for audio generation (default: 47.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | The modified positive conditioning with audio timing information applied |
| `negative` | CONDITIONING | The modified negative conditioning with audio timing information applied |
