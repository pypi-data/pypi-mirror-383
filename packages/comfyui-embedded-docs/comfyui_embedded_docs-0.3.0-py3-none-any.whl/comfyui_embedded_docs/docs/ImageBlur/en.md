The `ImageBlur` node applies a Gaussian blur to an image, allowing for the softening of edges and reduction of detail and noise. It provides control over the intensity and spread of the blur through parameters.

## Inputs

| Field          | Data Type | Description                                                                   |
|----------------|-------------|-------------------------------------------------------------------------------|
| `image`        | `IMAGE`     | The input image to be blurred. This is the primary target for the blur effect. |
| `blur_radius`  | `INT`       | Determines the radius of the blur effect. A larger radius results in a more pronounced blur. |
| `sigma`        | `FLOAT`     | Controls the spread of the blur. A higher sigma value means the blur will affect a wider area around each pixel. |

## Outputs

| Field | Data Type | Description                                                              |
|-------|-------------|--------------------------------------------------------------------------|
| `image`| `IMAGE`     | The output is the blurred version of the input image, with the degree of blur determined by the input parameters. |
