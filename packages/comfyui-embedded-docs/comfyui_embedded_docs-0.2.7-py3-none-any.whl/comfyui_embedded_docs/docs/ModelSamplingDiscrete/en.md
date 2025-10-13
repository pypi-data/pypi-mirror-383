
This node is designed to modify the sampling behavior of a model by applying a discrete sampling strategy. It allows for the selection of different sampling methods, such as epsilon, v_prediction, lcm, or x0, and optionally adjusts the model's noise reduction strategy based on the zero-shot noise ratio (zsnr) setting.

## Inputs

| Parameter | Data Type | Python dtype     | Description |
|-----------|--------------|-------------------|-------------|
| `model`   | MODEL     | `torch.nn.Module` | The model to which the discrete sampling strategy will be applied. This parameter is crucial as it defines the base model that will undergo modification. |
| `sampling`| COMBO[STRING] | `str`           | Specifies the discrete sampling method to be applied to the model. The choice of method affects how the model generates samples, offering different strategies for sampling. |
| `zsnr`    | `BOOLEAN`   | `bool`           | A boolean flag that, when enabled, adjusts the model's noise reduction strategy based on the zero-shot noise ratio. This can influence the quality and characteristics of the generated samples. |

## Outputs

| Parameter | Data Type | Python dtype     | Description |
|-----------|-------------|-------------------|-------------|
| `model`   | MODEL     | `torch.nn.Module` | The modified model with the applied discrete sampling strategy. This model is now equipped to generate samples using the specified method and adjustments. |
