> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TorchCompileModel/en.md)

The TorchCompileModel node applies PyTorch compilation to a model to optimize its performance. It creates a copy of the input model and wraps it with PyTorch's compilation functionality using the specified backend. This can improve the model's execution speed during inference.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model to be compiled and optimized |
| `backend` | STRING | Yes | "inductor"<br>"cudagraphs" | The PyTorch compilation backend to use for optimization |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The compiled model with PyTorch compilation applied |
