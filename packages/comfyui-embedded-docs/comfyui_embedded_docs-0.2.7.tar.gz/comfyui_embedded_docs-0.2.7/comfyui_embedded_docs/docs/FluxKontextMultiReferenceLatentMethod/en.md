> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/FluxKontextMultiReferenceLatentMethod/en.md)

The FluxKontextMultiReferenceLatentMethod node modifies conditioning data by setting a specific reference latents method. It appends the chosen method to the conditioning input, which affects how reference latents are processed in subsequent generation steps. This node is marked as experimental and is part of the Flux conditioning system.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `conditioning` | CONDITIONING | Yes | - | The conditioning data to be modified with the reference latents method |
| `reference_latents_method` | STRING | Yes | `"offset"`<br>`"index"`<br>`"uxo/uno"` | The method to use for reference latents processing. If "uxo" or "uso" is selected, it will be converted to "uxo" |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `conditioning` | CONDITIONING | The modified conditioning data with the reference latents method applied |
