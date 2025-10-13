This node is designed for preparing images for the outpainting process by adding padding around them. It adjusts the image dimensions to ensure compatibility with outpainting algorithms, facilitating the generation of extended image areas beyond the original boundaries.

## Inputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `image`   | `IMAGE`     | The 'image' input is the primary image to be prepared for outpainting, serving as the base for padding operations. |
| `left`    | `INT`       | Specifies the amount of padding to add to the left side of the image, influencing the expanded area for outpainting. |
| `top`     | `INT`       | Determines the amount of padding to add to the top of the image, affecting the vertical expansion for outpainting. |
| `right`   | `INT`       | Defines the amount of padding to add to the right side of the image, impacting the horizontal expansion for outpainting. |
| `bottom`  | `INT`       | Indicates the amount of padding to add to the bottom of the image, contributing to the vertical expansion for outpainting. |
| `feathering` | `INT` | Controls the smoothness of the transition between the original image and the added padding, enhancing the visual integration for outpainting. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `image`   | `IMAGE`     | The output 'image' represents the padded image, ready for the outpainting process. |
| `mask`    | `MASK`      | The output 'mask' indicates the areas of the original image and the added padding, useful for guiding the outpainting algorithms. |
