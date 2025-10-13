
SDTurboScheduler is designed to generate a sequence of sigma values for image sampling, adjusting the sequence based on the denoise level and the number of steps specified. It leverages a specific model's sampling capabilities to produce these sigma values, which are crucial for controlling the denoising process during image generation.

## Inputs

| Parameter | Data Type | Description |
| --- | --- | --- |
| `model` | `MODEL` | The model parameter specifies the generative model to be used for sigma value generation. It is crucial for determining the specific sampling behavior and capabilities of the scheduler. |
| `steps` | `INT` | The steps parameter determines the length of the sigma sequence to be generated, directly influencing the granularity of the denoising process. |
| `denoise` | `FLOAT` | The denoise parameter adjusts the starting point of the sigma sequence, allowing for finer control over the denoising level applied during image generation. |

## Outputs

| Parameter | Data Type | Description |
| --- | --- | --- |
| `sigmas` | `SIGMAS` | A sequence of sigma values generated based on the specified model, steps, and denoise level. These values are essential for controlling the denoising process in image generation. |
