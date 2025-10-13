
This node specializes in enhancing the resolution of images through a 4x upscale process, incorporating conditioning elements to refine the output. It leverages diffusion techniques to upscale images while allowing for the adjustment of scale ratio and noise augmentation to fine-tune the enhancement process.

## Inputs

| Parameter            | Comfy dtype        | Description |
|----------------------|--------------------|-------------|
| `images`             | `IMAGE`            | The input images to be upscaled. This parameter is crucial as it directly influences the quality and resolution of the output images. |
| `positive`           | `CONDITIONING`     | Positive conditioning elements that guide the upscale process towards desired attributes or features in the output images. |
| `negative`           | `CONDITIONING`     | Negative conditioning elements that the upscale process should avoid, helping to steer the output away from undesired attributes or features. |
| `scale_ratio`        | `FLOAT`            | Determines the factor by which the image resolution is increased. A higher scale ratio results in a larger output image, allowing for greater detail and clarity. |
| `noise_augmentation` | `FLOAT`            | Controls the level of noise augmentation applied during the upscale process. This can be used to introduce variability and improve the robustness of the output images. |

## Outputs

| Parameter     | Data Type | Description |
|---------------|--------------|-------------|
| `positive`    | `CONDITIONING` | The refined positive conditioning elements resulting from the upscale process. |
| `negative`    | `CONDITIONING` | The refined negative conditioning elements resulting from the upscale process. |
| `latent`      | `LATENT`     | A latent representation generated during the upscale process, which can be utilized in further processing or model training. |
