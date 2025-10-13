> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LatentApplyOperationCFG/en.md)

The LatentApplyOperationCFG node applies a latent operation to modify the conditioning guidance process in a model. It works by intercepting the conditioning outputs during the classifier-free guidance (CFG) sampling process and applying the specified operation to the latent representations before they are used for generation.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model to which the CFG operation will be applied |
| `operation` | LATENT_OPERATION | Yes | - | The latent operation to apply during the CFG sampling process |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with the CFG operation applied to its sampling process |
