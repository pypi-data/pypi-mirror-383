> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LTXVCropGuides/en.md)

The LTXVCropGuides node processes conditioning and latent inputs for video generation by removing keyframe information and adjusting the latent dimensions. It crops the latent image and noise mask to exclude keyframe sections while clearing keyframe indices from both positive and negative conditioning inputs. This prepares the data for video generation workflows that don't require keyframe guidance.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | The positive conditioning input containing guidance information for generation |
| `negative` | CONDITIONING | Yes | - | The negative conditioning input containing guidance information for what to avoid in generation |
| `latent` | LATENT | Yes | - | The latent representation containing image samples and noise mask data |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | The processed positive conditioning with keyframe indices cleared |
| `negative` | CONDITIONING | The processed negative conditioning with keyframe indices cleared |
| `latent` | LATENT | The cropped latent representation with adjusted samples and noise mask |
