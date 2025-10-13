> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CFGNorm/en.md)

The CFGNorm node applies a normalization technique to the classifier-free guidance (CFG) process in diffusion models. It adjusts the scale of the denoised prediction by comparing the norms of the conditional and unconditional outputs, then applies a strength multiplier to control the effect. This helps stabilize the generation process by preventing extreme values in the guidance scaling.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `model` | MODEL | required | - | - | The diffusion model to apply CFG normalization to |
| `strength` | FLOAT | required | 1.0 | 0.0 - 100.0 | Controls the intensity of the normalization effect applied to the CFG scaling |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `patched_model` | MODEL | Returns the modified model with CFG normalization applied to its sampling process |
