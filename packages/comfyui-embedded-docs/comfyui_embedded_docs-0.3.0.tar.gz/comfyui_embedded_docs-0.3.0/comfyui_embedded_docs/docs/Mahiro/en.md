> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/Mahiro/en.md)

The Mahiro node modifies the guidance function to focus more on the direction of the positive prompt rather than the difference between positive and negative prompts. It creates a patched model that applies a custom guidance scaling approach using cosine similarity between normalized conditional and unconditional denoised outputs. This experimental node helps steer the generation more strongly toward the positive prompt's intended direction.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | | The model to be patched with the modified guidance function |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `patched_model` | MODEL | The modified model with the Mahiro guidance function applied |
