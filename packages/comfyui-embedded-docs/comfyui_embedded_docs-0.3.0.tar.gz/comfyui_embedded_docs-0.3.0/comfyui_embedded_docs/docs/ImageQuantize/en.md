The ImageQuantize node is designed to reduce the number of colors in an image to a specified number, optionally applying dithering techniques to maintain visual quality. This process is useful for creating palette-based images or reducing the color complexity for certain applications.

## Inputs

| Field   | Data Type | Description                                                                       |
|---------|-------------|-----------------------------------------------------------------------------------|
| `image` | `IMAGE`     | The input image tensor to be quantized. It affects the node's execution by being the primary data upon which color reduction is performed. |
| `colors`| `INT`       | Specifies the number of colors to reduce the image to. It directly influences the quantization process by determining the color palette size. |
| `dither`| COMBO[STRING] | Determines the dithering technique to be applied during quantization, affecting the visual quality and appearance of the output image. |

## Outputs

| Field | Data Type | Description                                                                   |
|-------|-------------|-------------------------------------------------------------------------------|
| `image`| `IMAGE`     | The quantized version of the input image, with reduced color complexity and optionally dithered to maintain visual quality. |
