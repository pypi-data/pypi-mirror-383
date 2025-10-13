The KSamplerSelect node is designed to select a specific sampler based on the provided sampler name. It abstracts the complexity of sampler selection, allowing users to easily switch between different sampling strategies for their tasks.

## Inputs

| Parameter         | Data Type | Description                                                                                      |
|-------------------|-------------|------------------------------------------------------------------------------------------------|
| `sampler_name`    | COMBO[STRING] | Specifies the name of the sampler to be selected. This parameter determines which sampling strategy will be used, impacting the overall sampling behavior and results. |

## Outputs

| Parameter   | Data Type | Description                                                                 |
|-------------|-------------|-----------------------------------------------------------------------------|
| `sampler`   | `SAMPLER`   | Returns the selected sampler object, ready to be used for sampling tasks. |
