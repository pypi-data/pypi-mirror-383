This node is designed for compositing operations, specifically to join an image with its corresponding alpha mask to produce a single output image. It effectively combines visual content with transparency information, enabling the creation of images where certain areas are transparent or semi-transparent.

## Inputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `image`   | `IMAGE`     | The main visual content to be combined with an alpha mask. It represents the image without transparency information. |
| `alpha`   | `MASK`      | The alpha mask that defines the transparency of the corresponding image. It is used to determine which parts of the image should be transparent or semi-transparent. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `image`   | `IMAGE`     | The output is a single image that combines the input image with the alpha mask, incorporating transparency information into the visual content. |
