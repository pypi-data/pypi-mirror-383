
The PorterDuffImageComposite node is designed to perform image compositing using the Porter-Duff compositing operators. It allows for the combination of source and destination images according to various blending modes, enabling the creation of complex visual effects by manipulating image transparency and overlaying images in creative ways.

## Inputs

| Parameter | Data Type | Description |
| --------- | ------------ | ----------- |
| `source`  | `IMAGE`     | The source image tensor to be composited over the destination image. It plays a crucial role in determining the final visual outcome based on the selected compositing mode. |
| `source_alpha` | `MASK` | The alpha channel of the source image, which specifies the transparency of each pixel in the source image. It affects how the source image blends with the destination image. |
| `destination` | `IMAGE` | The destination image tensor that serves as the backdrop over which the source image is composited. It contributes to the final composited image based on the blending mode. |
| `destination_alpha` | `MASK` | The alpha channel of the destination image, defining the transparency of the destination image's pixels. It influences the blending of the source and destination images. |
| `mode` | COMBO[STRING] | The Porter-Duff compositing mode to apply, which determines how the source and destination images are blended together. Each mode creates different visual effects. |

## Outputs

| Parameter | Data Type | Description |
| --------- | ------------ | ----------- |
| `image`   | `IMAGE`     | The composited image resulting from the application of the specified Porter-Duff mode. |
| `mask`    | `MASK`      | The alpha channel of the composited image, indicating the transparency of each pixel. |
