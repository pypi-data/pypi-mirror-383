> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SelfAttentionGuidance/en.md)

The Self-Attention Guidance node applies guidance to diffusion models by modifying the attention mechanism during the sampling process. It captures attention scores from unconditional denoising steps and uses them to create blurred guidance maps that influence the final output. This technique helps guide the generation process by leveraging the model's own attention patterns.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The diffusion model to apply self-attention guidance to |
| `scale` | FLOAT | No | -2.0 to 5.0 | The strength of the self-attention guidance effect (default: 0.5) |
| `blur_sigma` | FLOAT | No | 0.0 to 10.0 | The amount of blur applied to create the guidance map (default: 2.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with self-attention guidance applied |

**Note:** This node is currently experimental and has limitations with chunked batches. It can only save attention scores from one UNet call and may not work properly with larger batch sizes.
