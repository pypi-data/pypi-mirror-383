> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LotusConditioning/en.md)

The LotusConditioning node provides pre-computed conditioning embeddings for the Lotus model. It uses a frozen encoder with null conditioning and returns hardcoded prompt embeddings to achieve parity with the reference implementation without requiring inference or loading large tensor files. This node outputs a fixed conditioning tensor that can be used directly in the generation pipeline.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| *No inputs* | - | - | - | This node does not accept any input parameters. |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `conditioning` | CONDITIONING | The pre-computed conditioning embeddings for the Lotus model, containing fixed prompt embeddings and an empty dictionary. |
