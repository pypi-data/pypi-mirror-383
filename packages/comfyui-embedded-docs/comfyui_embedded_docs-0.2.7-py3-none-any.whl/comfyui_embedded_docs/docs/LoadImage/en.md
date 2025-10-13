
The LoadImage node is designed to load and preprocess images from a specified path. It handles image formats with multiple frames, applies necessary transformations such as rotation based on EXIF data, normalizes pixel values, and optionally generates a mask for images with an alpha channel. This node is essential for preparing images for further processing or analysis within a pipeline.

## Inputs

| Parameter | Data Type | Description |
|-----------|--------------|-------------|
| `image`   | COMBO[STRING] | The 'image' parameter specifies the identifier of the image to be loaded and processed. It is crucial for determining the path to the image file and subsequently loading the image for transformation and normalization. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `image`   | `IMAGE`     | The processed image, with pixel values normalized and transformations applied as necessary. It is ready for further processing or analysis. |
| `mask`    | `MASK`      | An optional output providing a mask for the image, useful in scenarios where the image includes an alpha channel for transparency. |
