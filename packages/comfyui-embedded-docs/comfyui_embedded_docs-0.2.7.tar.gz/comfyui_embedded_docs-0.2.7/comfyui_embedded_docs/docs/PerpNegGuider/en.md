> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PerpNegGuider/en.md)

The PerpNegGuider node creates a guidance system for controlling image generation using perpendicular negative conditioning. It takes positive, negative, and empty conditioning inputs and applies a specialized guidance algorithm to steer the generation process. This node is designed for testing purposes and provides fine control over the guidance strength and negative scaling.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model to use for guidance generation |
| `positive` | CONDITIONING | Yes | - | The positive conditioning that guides the generation toward desired content |
| `negative` | CONDITIONING | Yes | - | The negative conditioning that guides the generation away from unwanted content |
| `empty_conditioning` | CONDITIONING | Yes | - | The empty or neutral conditioning used as a baseline reference |
| `cfg` | FLOAT | No | 0.0 - 100.0 | The classifier-free guidance scale that controls how strongly the conditioning influences the generation (default: 8.0) |
| `neg_scale` | FLOAT | No | 0.0 - 100.0 | The negative scaling factor that adjusts the strength of negative conditioning (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `guider` | GUIDER | A configured guidance system ready for use in the generation pipeline |
