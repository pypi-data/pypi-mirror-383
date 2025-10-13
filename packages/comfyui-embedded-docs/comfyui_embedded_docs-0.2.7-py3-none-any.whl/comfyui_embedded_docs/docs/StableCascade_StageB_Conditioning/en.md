> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StableCascade_StageB_Conditioning/en.md)

The StableCascade_StageB_Conditioning node prepares conditioning data for Stable Cascade Stage B generation by combining existing conditioning information with prior latent representations from Stage C. It modifies the conditioning data to include the latent samples from Stage C, enabling the generation process to leverage the prior information for more coherent outputs.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `conditioning` | CONDITIONING | Yes | - | The conditioning data to be modified with Stage C prior information |
| `stage_c` | LATENT | Yes | - | The latent representation from Stage C containing prior samples for conditioning |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `CONDITIONING` | CONDITIONING | The modified conditioning data with Stage C prior information integrated |
