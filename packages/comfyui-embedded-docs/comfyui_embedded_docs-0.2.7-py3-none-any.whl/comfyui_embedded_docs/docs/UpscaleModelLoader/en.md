This node will detect models located in the `ComfyUI/models/upscale_models` folder, and it will also read models from additional paths configured in the extra_model_paths.yaml file. Sometimes, you may need to **refresh the ComfyUI interface** to allow it to read the model files from the corresponding folder.

The UpscaleModelLoader node is designed for loading upscale models from a specified directory. It facilitates the retrieval and preparation of upscale models for image upscaling tasks, ensuring that the models are correctly loaded and configured for evaluation.

## Inputs

| Field          | Comfy dtype       | Description                                                                       |
|----------------|-------------------|-----------------------------------------------------------------------------------|
| `model_name`   | `COMBO[STRING]`    | Specifies the name of the upscale model to be loaded, identifying and retrieving the correct model file from the upscale models directory. |

## Outputs

| Field            | Comfy dtype         | Description                                                              |
|-------------------|---------------------|--------------------------------------------------------------------------|
| `upscale_model`  | `UPSCALE_MODEL`     | Returns the loaded and prepared upscale model, ready for use in image upscaling tasks. |
