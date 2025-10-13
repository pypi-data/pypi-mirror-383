> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanContextWindowsManual/en.md)

The WAN Context Windows (Manual) node allows you to manually configure context windows for WAN-like models with 2-dimensional processing. It applies custom context window settings during sampling by specifying the window length, overlap, scheduling method, and fusion technique. This gives you precise control over how the model processes information across different context regions.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model to apply context windows to during sampling. |
| `context_length` | INT | Yes | 1 to 1048576 | The length of the context window (default: 81). |
| `context_overlap` | INT | Yes | 0 to 1048576 | The overlap of the context window (default: 30). |
| `context_schedule` | COMBO | Yes | "static_standard"<br>"uniform_standard"<br>"uniform_looped"<br>"batched" | The stride of the context window. |
| `context_stride` | INT | Yes | 1 to 1048576 | The stride of the context window; only applicable to uniform schedules (default: 1). |
| `closed_loop` | BOOLEAN | Yes | - | Whether to close the context window loop; only applicable to looped schedules (default: False). |
| `fuse_method` | COMBO | Yes | "pyramid" | The method to use to fuse the context windows (default: "pyramid"). |

**Note:** The `context_stride` parameter only affects uniform schedules, and `closed_loop` only applies to looped schedules. The context length and overlap values are automatically adjusted to ensure minimum valid values during processing.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The model with the applied context window configuration. |
