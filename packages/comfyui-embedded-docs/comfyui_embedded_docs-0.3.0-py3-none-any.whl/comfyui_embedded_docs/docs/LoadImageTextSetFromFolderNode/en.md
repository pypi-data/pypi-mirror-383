> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LoadImageTextSetFromFolderNode/en.md)

Loads a batch of images and their corresponding text captions from a specified directory for training purposes. The node automatically searches for image files and their associated caption text files, processes the images according to specified resize settings, and encodes the captions using the provided CLIP model.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `folder` | STRING | Yes | - | The folder to load images from. |
| `clip` | CLIP | Yes | - | The CLIP model used for encoding the text. |
| `resize_method` | COMBO | No | "None"<br>"Stretch"<br>"Crop"<br>"Pad" | The method used to resize images (default: "None"). |
| `width` | INT | No | -1 to 10000 | The width to resize the images to. -1 means use the original width (default: -1). |
| `height` | INT | No | -1 to 10000 | The height to resize the images to. -1 means use the original height (default: -1). |

**Note:** The CLIP input must be valid and cannot be None. If the CLIP model comes from a checkpoint loader node, ensure the checkpoint contains a valid CLIP or text encoder model.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `IMAGE` | IMAGE | The batch of loaded and processed images. |
| `CONDITIONING` | CONDITIONING | The encoded conditioning data from the text captions. |
