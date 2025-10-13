
This node is designed to enhance a model's sampling capabilities by integrating continuous EDM (Energy-based Diffusion Models) sampling techniques. It allows for the dynamic adjustment of the noise levels within the model's sampling process, offering a more refined control over the generation quality and diversity.

## Inputs

| Parameter   | Data Type | Python dtype        | Description |
|-------------|--------------|----------------------|-------------|
| `model`     | `MODEL`     | `torch.nn.Module`   | The model to be enhanced with continuous EDM sampling capabilities. It serves as the foundation for applying the advanced sampling techniques. |
| `sampling`  | COMBO[STRING] | `str`             | Specifies the type of sampling to be applied, either 'eps' for epsilon sampling or 'v_prediction' for velocity prediction, influencing the model's behavior during the sampling process. |
| `sigma_max` | `FLOAT`     | `float`             | The maximum sigma value for noise level, allowing for upper bound control in the noise injection process during sampling. |
| `sigma_min` | `FLOAT`     | `float`             | The minimum sigma value for noise level, setting the lower limit for noise injection, thus affecting the model's sampling precision. |

## Outputs

| Parameter | Data Type | Python dtype        | Description |
|-----------|-------------|----------------------|-------------|
| `model`   | MODEL     | `torch.nn.Module`   | The enhanced model with integrated continuous EDM sampling capabilities, ready for further use in generation tasks. |
