> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CLIPMergeAdd/en.md)

The CLIPMergeAdd node combines two CLIP models by adding patches from the second model to the first model. It creates a copy of the first CLIP model and selectively incorporates key patches from the second model, excluding position IDs and logit scale parameters. This allows you to merge CLIP model components while preserving the structure of the base model.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `clip1` | CLIP | Yes | - | The base CLIP model that will be cloned and used as the foundation for merging |
| `clip2` | CLIP | Yes | - | The secondary CLIP model that provides key patches to be added to the base model |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `CLIP` | CLIP | A merged CLIP model containing the base model structure with added patches from the secondary model |
