This node will detect models located in the `ComfyUI/models/checkpoints` folder, and it will also read models from additional paths configured in the extra_model_paths.yaml file. Sometimes, you may need to **refresh the ComfyUI interface** to allow it to read the model files from the corresponding folder.

The unCLIPCheckpointLoader node is designed for loading checkpoints specifically tailored for unCLIP models. It facilitates the retrieval and initialization of models, CLIP vision modules, and VAEs from a specified checkpoint, streamlining the setup process for further operations or analyses.

## Inputs

| Field      | Comfy dtype       | Description                                                                       |
|------------|-------------------|-----------------------------------------------------------------------------------|
| `ckpt_name`| `COMBO[STRING]`    | Specifies the name of the checkpoint to be loaded, identifying and retrieving the correct checkpoint file from a predefined directory, determining the initialization of models and configurations. |

## Outputs

| Field       | Comfy dtype   | Description                                                              | Python dtype         |
|-------------|---------------|--------------------------------------------------------------------------|---------------------|
| `model`     | `MODEL`       | Represents the primary model loaded from the checkpoint.                   | `torch.nn.Module`   |
| `clip`      | `CLIP`        | Represents the CLIP module loaded from the checkpoint, if available.      | `torch.nn.Module`   |
| `vae`       | `VAE`         | Represents the VAE module loaded from the checkpoint, if available.        | `torch.nn.Module`   |
| `clip_vision`| `CLIP_VISION` | Represents the CLIP vision module loaded from the checkpoint, if available.| `torch.nn.Module`   |
