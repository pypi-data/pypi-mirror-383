The `ImageColorToMask` node is designed to convert a specified color in an image to a mask. It processes an image and a target color, generating a mask where the specified color is highlighted, facilitating operations like color-based segmentation or object isolation.

## Inputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `image`   | `IMAGE`     | The 'image' parameter represents the input image to be processed. It is crucial for determining the areas of the image that match the specified color to be converted into a mask. |
| `color`   | `INT`       | The 'color' parameter specifies the target color in the image to be converted into a mask. It plays a key role in identifying the specific color areas to be highlighted in the resulting mask. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `mask`    | `MASK`      | The output is a mask highlighting the areas of the input image that match the specified color. This mask can be used for further image processing tasks, such as segmentation or object isolation. |
