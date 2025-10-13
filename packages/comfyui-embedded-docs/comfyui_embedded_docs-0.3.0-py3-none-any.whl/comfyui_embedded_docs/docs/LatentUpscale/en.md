
The LatentUpscale node is designed for upscaling latent representations of images. It allows for the adjustment of the output image's dimensions and the method of upscaling, providing flexibility in enhancing the resolution of latent images.

## Inputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `samples` | `LATENT`    | The latent representation of an image to be upscaled. This parameter is crucial for determining the starting point of the upscaling process. |
| `upscale_method` | COMBO[STRING] | Specifies the method used for upscaling the latent image. Different methods can affect the quality and characteristics of the upscaled image. |
| `width`   | `INT`       | The desired width of the upscaled image. If set to 0, it will be calculated based on the height to maintain the aspect ratio. |
| `height`  | `INT`       | The desired height of the upscaled image. If set to 0, it will be calculated based on the width to maintain the aspect ratio. |
| `crop`    | COMBO[STRING] | Determines how the upscaled image should be cropped, affecting the final appearance and dimensions of the output. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `latent`  | `LATENT`    | The upscaled latent representation of the image, ready for further processing or generation. |
