> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LatentConcat/en.md)

The LatentConcat node combines two latent samples along a specified dimension. It takes two latent inputs and concatenates them together along the chosen axis (x, y, or t dimension). The node automatically adjusts the batch size of the second input to match the first input before performing the concatenation operation.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `samples1` | LATENT | Yes | - | The first latent sample to concatenate |
| `samples2` | LATENT | Yes | - | The second latent sample to concatenate |
| `dim` | COMBO | Yes | `"x"`<br>`"-x"`<br>`"y"`<br>`"-y"`<br>`"t"`<br>`"-t"` | The dimension along which to concatenate the latent samples. Positive values concatenate samples1 before samples2, negative values concatenate samples2 before samples1 |

**Note:** The second latent sample (`samples2`) is automatically adjusted to match the batch size of the first latent sample (`samples1`) before concatenation.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | LATENT | The concatenated latent samples resulting from combining the two input samples along the specified dimension |
