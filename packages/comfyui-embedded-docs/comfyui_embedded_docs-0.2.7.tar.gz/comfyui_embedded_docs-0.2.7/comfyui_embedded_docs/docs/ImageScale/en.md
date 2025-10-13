The ImageScale node is designed for resizing images to specific dimensions, offering a selection of upscale methods and the ability to crop the resized image. It abstracts the complexity of image upscaling and cropping, providing a straightforward interface for modifying image dimensions according to user-defined parameters.

## Inputs

| Parameter       | Data Type | Description                                                                           |
|-----------------|-------------|---------------------------------------------------------------------------------------|
| `image`         | `IMAGE`     | The input image to be upscaled. This parameter is central to the node's operation, serving as the primary data upon which resizing transformations are applied. The quality and dimensions of the output image are directly influenced by the original image's properties. |
| `upscale_method`| COMBO[STRING] | Specifies the method used for upscaling the image. The choice of method can affect the quality and characteristics of the upscaled image, influencing the visual fidelity and potential artifacts in the resized output. |
| `width`         | `INT`       | The target width for the upscaled image. This parameter directly influences the dimensions of the output image, determining the horizontal scale of the resizing operation. |
| `height`        | `INT`       | The target height for the upscaled image. This parameter directly influences the dimensions of the output image, determining the vertical scale of the resizing operation. |
| `crop`          | COMBO[STRING] | Determines whether and how the upscaled image should be cropped, offering options for disabled cropping or center cropping. This affects the final composition of the image by potentially removing edges to fit the specified dimensions. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `image`   | `IMAGE`     | The upscaled (and optionally cropped) image, ready for further processing or visualization. |
