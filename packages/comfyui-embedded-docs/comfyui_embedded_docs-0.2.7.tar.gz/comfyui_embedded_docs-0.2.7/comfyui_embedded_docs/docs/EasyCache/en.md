> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/EasyCache/en.md)

The EasyCache node implements a native caching system for models to improve performance by reusing previously computed steps during the sampling process. It adds EasyCache functionality to a model with configurable thresholds for when to start and stop using the cache during the sampling timeline.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model to add EasyCache to. |
| `reuse_threshold` | FLOAT | No | 0.0 - 3.0 | The threshold for reusing cached steps (default: 0.2). |
| `start_percent` | FLOAT | No | 0.0 - 1.0 | The relative sampling step to begin use of EasyCache (default: 0.15). |
| `end_percent` | FLOAT | No | 0.0 - 1.0 | The relative sampling step to end use of EasyCache (default: 0.95). |
| `verbose` | BOOLEAN | No | - | Whether to log verbose information (default: False). |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The model with EasyCache functionality added. |
