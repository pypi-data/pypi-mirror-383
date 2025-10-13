This node will detect models located in the `ComfyUI/models/gligen` folder, and it will also read models from additional paths configured in the extra_model_paths.yaml file. Sometimes, you may need to **refresh the ComfyUI interface** to allow it to read the model files from the corresponding folder.

The `GLIGENLoader` node is designed for loading GLIGEN models, which are specialized generative models. It facilitates the process of retrieving and initializing these models from specified paths, making them ready for further generative tasks.

## Inputs

| Field       | Comfy dtype       | Description                                                                       |
|-------------|-------------------|-----------------------------------------------------------------------------------|
| `gligen_name`| `COMBO[STRING]`    | The name of the GLIGEN model to be loaded, specifying which model file to retrieve and load, crucial for the initialization of the GLIGEN model. |

## Outputs

| Field    | Data Type | Description                                                              |
|----------|-------------|--------------------------------------------------------------------------|
| `gligen` | `GLIGEN`    | The loaded GLIGEN model, ready for use in generative tasks, representing the fully initialized model loaded from the specified path. |
