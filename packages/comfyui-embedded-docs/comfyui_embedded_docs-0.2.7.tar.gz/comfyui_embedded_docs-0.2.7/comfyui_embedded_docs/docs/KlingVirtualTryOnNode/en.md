> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/KlingVirtualTryOnNode/en.md)

Kling Virtual Try On Node. Input a human image and a cloth image to try on the cloth on the human. You can merge multiple clothing item pictures into one image with a white background.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `human_image` | IMAGE | Yes | - | The human image to try clothes on |
| `cloth_image` | IMAGE | Yes | - | The clothing image to try on the human |
| `model_name` | STRING | Yes | `"kolors-virtual-try-on-v1"` | The virtual try-on model to use (default: "kolors-virtual-try-on-v1") |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | IMAGE | The resulting image showing the human with the clothing item tried on |
