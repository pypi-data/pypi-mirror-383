
This node is designed for encoding images into a latent space representation using a specified VAE model. It abstracts the complexity of the encoding process, providing a straightforward way to transform images into their latent representations.

## Inputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `pixels`  | `IMAGE`     | The 'pixels' parameter represents the image data to be encoded into the latent space. It plays a crucial role in determining the output latent representation by serving as the direct input for the encoding process. |
| `vae`     | VAE       | The 'vae' parameter specifies the Variational Autoencoder model to be used for encoding the image data into latent space. It is essential for defining the encoding mechanism and characteristics of the generated latent representation. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `latent`  | `LATENT`    | The output is a latent space representation of the input image, encapsulating its essential features in a compressed form. |
