This node will detect models located in the `ComfyUI/models/controlnet` folder, and it will also read models from additional paths configured in the extra_model_paths.yaml file. Sometimes, you may need to **refresh the ComfyUI interface** to allow it to read the model files from the corresponding folder.

The DiffControlNetLoader node is designed for loading differential control networks, which are specialized models that can modify the behavior of another model based on control net specifications. This node allows for the dynamic adjustment of model behaviors by applying differential control nets, facilitating the creation of customized model outputs.

## Inputs

| Field               | Comfy dtype       | Description                                                                                 |
|---------------------|-------------------|---------------------------------------------------------------------------------------------|
| `model`             | `MODEL`           | The base model to which the differential control net will be applied, allowing for customization of the model's behavior. |
| `control_net_name`  | `COMBO[STRING]`    | Identifies the specific differential control net to be loaded and applied to the base model for modifying its behavior. |

## Outputs

| Field          | Comfy dtype   | Description                                                                   |
|----------------|---------------|-------------------------------------------------------------------------------|
| `control_net`  | `CONTROL_NET` | A differential control net that has been loaded and is ready to be applied to a base model for behavior modification. |
