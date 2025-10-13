> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PerpNeg/en.md)

The PerpNeg node applies perpendicular negative guidance to a model's sampling process. This node modifies the model's configuration function to adjust noise predictions using negative conditioning and scaling factors. It has been deprecated and replaced by the PerpNegGuider node for improved functionality.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model to apply perpendicular negative guidance to |
| `empty_conditioning` | CONDITIONING | Yes | - | Empty conditioning used for negative guidance calculations |
| `neg_scale` | FLOAT | No | 0.0 - 100.0 | Scaling factor for negative guidance (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with perpendicular negative guidance applied |

**Note**: This node is deprecated and has been replaced by PerpNegGuider. It is marked as experimental and should not be used in production workflows.
