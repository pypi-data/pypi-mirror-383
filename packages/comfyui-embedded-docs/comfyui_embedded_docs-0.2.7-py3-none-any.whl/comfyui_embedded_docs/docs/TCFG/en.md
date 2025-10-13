> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TCFG/en.md)

TCFG (Tangential Damping CFG) implements a guidance technique that refines the unconditional (negative) predictions to better align with the conditional (positive) predictions. This method improves output quality by applying tangential damping to the unconditional guidance, based on the research paper referenced as 2503.18137. The node modifies the model's sampling behavior by adjusting how unconditional predictions are processed during the classifier-free guidance process.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model to apply tangential damping CFG to |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `patched_model` | MODEL | The modified model with tangential damping CFG applied |
