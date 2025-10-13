> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PerturbedAttentionGuidance/en.md)

The PerturbedAttentionGuidance node applies perturbed attention guidance to a diffusion model to enhance generation quality. It modifies the model's self-attention mechanism during sampling by replacing it with a simplified version that focuses on value projections. This technique helps improve the coherence and quality of generated images by adjusting the conditional denoising process.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The diffusion model to apply perturbed attention guidance to |
| `scale` | FLOAT | No | 0.0 - 100.0 | The strength of the perturbed attention guidance effect (default: 3.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with perturbed attention guidance applied |
