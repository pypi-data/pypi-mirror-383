> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/VideoTriangleCFGGuidance/en.md)

The VideoTriangleCFGGuidance node applies a triangular classifier-free guidance scaling pattern to video models. It modifies the conditioning scale over time using a triangular wave function that oscillates between the minimum CFG value and the original conditioning scale. This creates a dynamic guidance pattern that can help improve video generation consistency and quality.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The video model to apply triangular CFG guidance to |
| `min_cfg` | FLOAT | Yes | 0.0 - 100.0 | The minimum CFG scale value for the triangular pattern (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with triangular CFG guidance applied |
