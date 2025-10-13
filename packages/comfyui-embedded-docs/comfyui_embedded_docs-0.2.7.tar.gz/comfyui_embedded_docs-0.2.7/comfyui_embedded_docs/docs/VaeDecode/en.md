
The VAEDecode node is designed for decoding latent representations into images using a specified Variational Autoencoder (VAE). It serves the purpose of generating images from compressed data representations, facilitating the reconstruction of images from their latent space encodings.

## Inputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `samples` | `LATENT`    | The 'samples' parameter represents the latent representations to be decoded into images. It is crucial for the decoding process as it provides the compressed data from which the images are reconstructed. |
| `vae`     | VAE       | The 'vae' parameter specifies the Variational Autoencoder model to be used for decoding the latent representations into images. It is essential for determining the decoding mechanism and the quality of the reconstructed images. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `image`   | `IMAGE`     | The output is an image reconstructed from the provided latent representation using the specified VAE model. |
