> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LazyCache/en.md)

LazyCache is a homebrew version of EasyCache that provides an even easier implementation. It works with any model in ComfyUI and adds caching functionality to reduce computation during sampling. While it generally performs worse than EasyCache, it can be more effective in some rare cases and offers universal compatibility.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model to add LazyCache to. |
| `reuse_threshold` | FLOAT | No | 0.0 - 3.0 | The threshold for reusing cached steps (default: 0.2). |
| `start_percent` | FLOAT | No | 0.0 - 1.0 | The relative sampling step to begin use of LazyCache (default: 0.15). |
| `end_percent` | FLOAT | No | 0.0 - 1.0 | The relative sampling step to end use of LazyCache (default: 0.95). |
| `verbose` | BOOLEAN | No | - | Whether to log verbose information (default: False). |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The model with LazyCache functionality added. |
