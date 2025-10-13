The ImageScaleBy node is designed for upscaling images by a specified scale factor using various interpolation methods. It allows for the adjustment of the image size in a flexible manner, catering to different upscaling needs.

## Inputs

| Parameter       | Data Type | Description                                                                 |
|-----------------|-------------|----------------------------------------------------------------------------|
| `image`         | `IMAGE`     | The input image to be upscaled. This parameter is crucial as it provides the base image that will undergo the upscaling process. |
| `upscale_method`| COMBO[STRING] | Specifies the interpolation method to be used for upscaling. The choice of method can affect the quality and characteristics of the upscaled image. |
| `scale_by`      | `FLOAT`     | The factor by which the image will be upscaled. This determines the increase in size of the output image relative to the input image. |

## Outputs

| Parameter | Data Type | Description                                                   |
|-----------|-------------|---------------------------------------------------------------|
| `image`   | `IMAGE`     | The upscaled image, which is larger than the input image according to the specified scale factor and interpolation method. |
