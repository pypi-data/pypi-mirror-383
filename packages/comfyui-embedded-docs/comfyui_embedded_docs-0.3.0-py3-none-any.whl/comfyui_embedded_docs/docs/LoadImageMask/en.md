
The LoadImageMask node is designed to load images and their associated masks from a specified path, processing them to ensure compatibility with further image manipulation or analysis tasks. It focuses on handling various image formats and conditions, such as presence of an alpha channel for masks, and prepares the images and masks for downstream processing by converting them to a standardized format.

## Inputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `image`   | COMBO[STRING] | The 'image' parameter specifies the image file to be loaded and processed. It plays a crucial role in determining the output by providing the source image for mask extraction and format conversion. |
| `channel` | COMBO[STRING] | The 'channel' parameter specifies the color channel of the image that will be used to generate the mask. This allows for flexibility in mask creation based on different color channels, enhancing the node's utility in various image processing scenarios. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `mask`    | `MASK`      | This node outputs the mask generated from the specified image and channel, prepared in a standardized format suitable for further processing in image manipulation tasks. |
