The LatentComposite node is designed to blend or merge two latent representations into a single output. This process is essential for creating composite images or features by combining the characteristics of the input latents in a controlled manner.

## Inputs

| Parameter    | Data Type | Description |
|--------------|-------------|-------------|
| `samples_to` | `LATENT`    | The 'samples_to' latent representation where the 'samples_from' will be composited onto. It serves as the base for the composite operation. |
| `samples_from` | `LATENT` | The 'samples_from' latent representation to be composited onto the 'samples_to'. It contributes its features or characteristics to the final composite output. |
| `x`          | `INT`      | The x-coordinate (horizontal position) where the 'samples_from' latent will be placed on the 'samples_to'. It determines the horizontal alignment of the composite. |
| `y`          | `INT`      | The y-coordinate (vertical position) where the 'samples_from' latent will be placed on the 'samples_to'. It determines the vertical alignment of the composite. |
| `feather`    | `INT`      | A boolean indicating whether the 'samples_from' latent should be resized to match the 'samples_to' before compositing. This can affect the scale and proportion of the composite result. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `latent`  | `LATENT`    | The output is a composite latent representation, blending the features of both 'samples_to' and 'samples_from' latents based on the specified coordinates and resizing option. |
