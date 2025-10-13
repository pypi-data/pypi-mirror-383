> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ContextWindowsManual/en.md)

The Context Windows (Manual) node allows you to manually configure context windows for models during sampling. It creates overlapping context segments with specified length, overlap, and scheduling patterns to process data in manageable chunks while maintaining continuity between segments.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model to apply context windows to during sampling. |
| `context_length` | INT | No | 1+ | The length of the context window (default: 16). |
| `context_overlap` | INT | No | 0+ | The overlap of the context window (default: 4). |
| `context_schedule` | COMBO | No | `STATIC_STANDARD`<br>`UNIFORM_STANDARD`<br>`UNIFORM_LOOPED`<br>`BATCHED` | The stride of the context window. |
| `context_stride` | INT | No | 1+ | The stride of the context window; only applicable to uniform schedules (default: 1). |
| `closed_loop` | BOOLEAN | No | - | Whether to close the context window loop; only applicable to looped schedules (default: False). |
| `fuse_method` | COMBO | No | `PYRAMID`<br>`LIST_STATIC` | The method to use to fuse the context windows (default: PYRAMID). |
| `dim` | INT | No | 0-5 | The dimension to apply the context windows to (default: 0). |

**Parameter Constraints:**

- `context_stride` is only used when uniform schedules are selected
- `closed_loop` is only applicable to looped schedules
- `dim` must be between 0 and 5 inclusive

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The model with context windows applied during sampling. |
