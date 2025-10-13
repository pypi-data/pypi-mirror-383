> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ThresholdMask/en.md)

The ThresholdMask node converts a mask to a binary mask by applying a threshold value. It compares each pixel in the input mask against the specified threshold value and creates a new mask where pixels above the threshold become 1 (white) and pixels below or equal to the threshold become 0 (black).

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `mask` | MASK | Yes | - | The input mask to be processed |
| `value` | FLOAT | Yes | 0.0 - 1.0 | The threshold value for binarization (default: 0.5) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `mask` | MASK | The resulting binary mask after thresholding |
