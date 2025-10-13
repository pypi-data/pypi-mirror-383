> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LTXVConditioning/en.md)

The LTXVConditioning node adds frame rate information to both positive and negative conditioning inputs for video generation models. It takes existing conditioning data and applies the specified frame rate value to both conditioning sets, making them suitable for video model processing.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | The positive conditioning input that will receive the frame rate information |
| `negative` | CONDITIONING | Yes | - | The negative conditioning input that will receive the frame rate information |
| `frame_rate` | FLOAT | No | 0.0 - 1000.0 | The frame rate value to apply to both conditioning sets (default: 25.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | The positive conditioning with frame rate information applied |
| `negative` | CONDITIONING | The negative conditioning with frame rate information applied |
