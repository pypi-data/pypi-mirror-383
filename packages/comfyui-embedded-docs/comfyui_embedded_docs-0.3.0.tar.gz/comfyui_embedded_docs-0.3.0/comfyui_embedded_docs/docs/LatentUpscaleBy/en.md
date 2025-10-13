
The LatentUpscaleBy node is designed for upscaling latent representations of images. It allows for the adjustment of the scale factor and the method of upscaling, providing flexibility in enhancing the resolution of latent samples.

## Inputs

| Parameter     | Data Type | Description |
|---------------|--------------|-------------|
| `samples`     | `LATENT`     | The latent representation of images to be upscaled. This parameter is crucial for determining the input data that will undergo the upscaling process. |
| `upscale_method` | COMBO[STRING] | Specifies the method used for upscaling the latent samples. The choice of method can significantly affect the quality and characteristics of the upscaled output. |
| `scale_by`    | `FLOAT`      | Determines the factor by which the latent samples are scaled. This parameter directly influences the resolution of the output, allowing for precise control over the upscaling process. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `latent`  | `LATENT`    | The upscaled latent representation, ready for further processing or generation tasks. This output is essential for enhancing the resolution of generated images or for subsequent model operations. |
