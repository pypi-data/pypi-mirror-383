The ImageScaleToTotalPixels node is designed for resizing images to a specified total number of pixels while maintaining the aspect ratio. It provides various methods for upscaling the image to achieve the desired pixel count.

## Inputs

| Parameter       | Data Type | Description                                                                |
|-----------------|-------------|----------------------------------------------------------------------------|
| `image`         | `IMAGE`     | The input image to be upscaled to the specified total number of pixels.    |
| `upscale_method`| COMBO[STRING] | The method used for upscaling the image. It affects the quality and characteristics of the upscaled image. |
| `megapixels`    | `FLOAT`     | The target size of the image in megapixels. This determines the total number of pixels in the upscaled image. |

## Outputs

| Parameter | Data Type | Description                                                           |
|-----------|-------------|-----------------------------------------------------------------------|
| `image`   | `IMAGE`     | The upscaled image with the specified total number of pixels, maintaining the original aspect ratio. |
