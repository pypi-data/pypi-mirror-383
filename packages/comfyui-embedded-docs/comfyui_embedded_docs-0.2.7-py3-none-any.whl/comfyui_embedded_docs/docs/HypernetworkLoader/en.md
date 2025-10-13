This node will detect models located in the `ComfyUI/models/hypernetworks` folder, and it will also read models from additional paths configured in the extra_model_paths.yaml file. Sometimes, you may need to **refresh the ComfyUI interface** to allow it to read the model files from the corresponding folder.

The HypernetworkLoader node is designed to enhance or modify the capabilities of a given model by applying a hypernetwork. It loads a specified hypernetwork and applies it to the model, potentially altering its behavior or performance based on the strength parameter. This process allows for dynamic adjustments to the model's architecture or parameters, enabling more flexible and adaptive AI systems.

## Inputs

| Field                 | Comfy dtype       | Description                                                                                  |
|-----------------------|-------------------|----------------------------------------------------------------------------------------------|
| `model`               | `MODEL`           | The base model to which the hypernetwork will be applied, determining the architecture to be enhanced or modified. |
| `hypernetwork_name`  | `COMBO[STRING]`   | The name of the hypernetwork to be loaded and applied to the model, impacting the model's modified behavior or performance. |
| `strength`            | `FLOAT`           | A scalar adjusting the intensity of the hypernetwork's effect on the model, allowing fine-tuning of the alterations. |

## Outputs

| Field   | Data Type | Description                                                              |
|---------|-------------|--------------------------------------------------------------------------|
| `model` | `MODEL`     | The modified model after the hypernetwork has been applied, showcasing the impact of the hypernetwork on the original model. |
