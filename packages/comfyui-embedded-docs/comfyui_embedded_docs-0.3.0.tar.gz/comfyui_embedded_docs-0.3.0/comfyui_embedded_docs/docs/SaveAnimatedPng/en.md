
The SaveAnimatedPNG node is designed for creating and saving animated PNG images from a sequence of frames. It handles the assembly of individual image frames into a cohesive animation, allowing for customization of frame duration, looping, and metadata inclusion.

## Inputs

| Field             | Data Type | Description                                                                         |
|-------------------|-------------|-------------------------------------------------------------------------------------|
| `images`          | `IMAGE`     | A list of images to be processed and saved as an animated PNG. Each image in the list represents a frame in the animation. |
| `filename_prefix` | `STRING`    | Specifies the base name for the output file, which will be used as a prefix for the generated animated PNG files. |
| `fps`             | `FLOAT`     | The frames per second rate for the animation, controlling how quickly the frames are displayed. |
| `compress_level`  | `INT`       | The level of compression applied to the animated PNG files, affecting file size and image clarity. |

## Outputs

| Field | Data Type | Description                                                                       |
|-------|-------------|-----------------------------------------------------------------------------------|
| `ui`  | N/A         | Provides a UI component displaying the generated animated PNG images and indicating whether the animation is single-frame or multi-frame. |
