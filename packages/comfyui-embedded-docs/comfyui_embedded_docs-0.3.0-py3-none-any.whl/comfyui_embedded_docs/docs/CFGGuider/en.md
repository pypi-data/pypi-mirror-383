> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CFGGuider/en.md)

The CFGGuider node creates a guidance system for controlling the sampling process in image generation. It takes a model along with positive and negative conditioning inputs, then applies a classifier-free guidance scale to steer the generation toward desired content while avoiding unwanted elements. This node outputs a guider object that can be used by sampling nodes to control the image generation direction.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `model` | MODEL | Required | - | - | The model to be used for guidance |
| `positive` | CONDITIONING | Required | - | - | The positive conditioning that guides the generation toward desired content |
| `negative` | CONDITIONING | Required | - | - | The negative conditioning that steers the generation away from unwanted content |
| `cfg` | FLOAT | Required | 8.0 | 0.0 - 100.0 | The classifier-free guidance scale that controls how strongly the conditioning influences the generation |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `GUIDER` | GUIDER | A guider object that can be passed to sampling nodes to control the generation process |
