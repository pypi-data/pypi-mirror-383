
The LatentCompositeMasked node is designed for blending two latent representations together at specified coordinates, optionally using a mask for more controlled compositing. This node enables the creation of complex latent images by overlaying parts of one image onto another, with the ability to resize the source image for a perfect fit.

## Inputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `destination` | `LATENT`    | The latent representation onto which another latent representation will be composited. Acts as the base layer for the composite operation. |
| `source` | `LATENT`    | The latent representation to be composited onto the destination. This source layer can be resized and positioned according to the specified parameters. |
| `x` | `INT`       | The x-coordinate in the destination latent representation where the source will be placed. Allows for precise positioning of the source layer. |
| `y` | `INT`       | The y-coordinate in the destination latent representation where the source will be placed, enabling accurate overlay positioning. |
| `resize_source` | `BOOLEAN` | A boolean flag indicating whether the source latent representation should be resized to match the destination's dimensions before compositing. |
| `mask` | `MASK`     | An optional mask that can be used to control the blending of the source onto the destination. The mask defines which parts of the source will be visible in the final composite. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `latent`  | `LATENT`    | The resulting latent representation after compositing the source onto the destination, potentially using a mask for selective blending. |
