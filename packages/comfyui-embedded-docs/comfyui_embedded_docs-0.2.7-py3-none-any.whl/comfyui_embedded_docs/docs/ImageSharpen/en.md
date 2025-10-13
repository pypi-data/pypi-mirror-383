The ImageSharpen node enhances the clarity of an image by accentuating its edges and details. It applies a sharpening filter to the image, which can be adjusted in intensity and radius, thereby making the image appear more defined and crisp.

## Inputs

| Field          | Data Type | Description                                                                                   |
|----------------|-------------|-----------------------------------------------------------------------------------------------|
| `image`        | `IMAGE`     | The input image to be sharpened. This parameter is crucial as it determines the base image on which the sharpening effect will be applied. |
| `sharpen_radius`| `INT`       | Defines the radius of the sharpening effect. A larger radius means that more pixels around the edge will be affected, leading to a more pronounced sharpening effect. |
| `sigma`        | `FLOAT`     | Controls the spread of the sharpening effect. A higher sigma value results in a smoother transition at the edges, while a lower sigma makes the sharpening more localized. |
| `alpha`        | `FLOAT`     | Adjusts the intensity of the sharpening effect. Higher alpha values result in a stronger sharpening effect. |

## Outputs

| Field | Data Type | Description                                                              |
|-------|-------------|--------------------------------------------------------------------------|
| `image`| `IMAGE`     | The sharpened image, with enhanced edges and details, ready for further processing or display. |
