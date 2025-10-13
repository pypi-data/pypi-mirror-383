
This node is designed for encoding images into a latent representation suitable for inpainting tasks, incorporating additional preprocessing steps to adjust the input image and mask for optimal encoding by the VAE model.

## Inputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `pixels`  | `IMAGE`     | The input image to be encoded. This image undergoes preprocessing and resizing to match the VAE model's expected input dimensions before encoding. |
| `vae`     | VAE       | The VAE model used for encoding the image into its latent representation. It plays a crucial role in the transformation process, determining the quality and characteristics of the output latent space. |
| `mask`    | `MASK`      | A mask indicating the regions of the input image to be inpainted. It is used to modify the image before encoding, ensuring that the VAE focuses on the relevant areas. |
| `grow_mask_by` | `INT` | Specifies how much to expand the inpainting mask to ensure seamless transitions in the latent space. A larger value increases the area affected by inpainting. |

## Outputs

| Parameter | Data Type | Description |
|-----------|-------------|-------------|
| `latent`  | `LATENT`    | The output includes the encoded latent representation of the image and a noise mask, both crucial for subsequent inpainting tasks. |
