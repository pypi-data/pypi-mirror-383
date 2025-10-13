This node scales the input image to an optimal size used during Flux Kontext model training using the Lanczos algorithm, based on the input image's aspect ratio. This node is particularly useful when inputting large-sized images, as oversized inputs may lead to degraded model output quality or issues such as multiple subjects appearing in the output.

## Inputs

| Parameter Name | Data Type | Input Type | Default Value | Value Range | Description |
|----------------|-----------|------------|---------------|-------------|-------------|
| `image` | IMAGE | Required | - | - | Input image to be resized |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `image` | IMAGE | Resized image |

## Preset Size List

The following is a list of standard sizes used during model training. The node will select the size closest to the input image's aspect ratio:

| Width | Height | Aspect Ratio |
|-------|--------|--------------|
| 672   | 1568   | 0.429       |
| 688   | 1504   | 0.457       |
| 720   | 1456   | 0.494       |
| 752   | 1392   | 0.540       |
| 800   | 1328   | 0.603       |
| 832   | 1248   | 0.667       |
| 880   | 1184   | 0.743       |
| 944   | 1104   | 0.855       |
| 1024  | 1024   | 1.000       |
| 1104  | 944    | 1.170       |
| 1184  | 880    | 1.345       |
| 1248  | 832    | 1.500       |
| 1328  | 800    | 1.660       |
| 1392  | 752    | 1.851       |
| 1456  | 720    | 2.022       |
| 1504  | 688    | 2.186       |
| 1568  | 672    | 2.333       |
