
The SplitImageWithAlpha node is designed to separate the color and alpha components of an image. It processes an input image tensor, extracting the RGB channels as the color component and the alpha channel as the transparency component, facilitating operations that require manipulation of these distinct image aspects.

## Inputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `image`   | `IMAGE`     | The 'image' parameter represents the input image tensor from which the RGB and alpha channels are to be separated. It is crucial for the operation as it provides the source data for the split. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `image`   | `IMAGE`     | The 'image' output represents the separated RGB channels of the input image, providing the color component without the transparency information. |
| `mask`    | `MASK`      | The 'mask' output represents the separated alpha channel of the input image, providing the transparency information. |
