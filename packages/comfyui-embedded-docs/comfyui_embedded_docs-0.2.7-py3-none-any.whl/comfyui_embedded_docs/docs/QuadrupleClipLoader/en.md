The Quadruple CLIP Loader, QuadrupleCLIPLoader, is one of the core nodes of ComfyUI, first added to support the HiDream I1 version model. If you find this node missing, try updating ComfyUI to the latest version to ensure node support.

It requires 4 CLIP models, corresponding to the parameters `clip_name1`, `clip_name2`, `clip_name3`, and `clip_name4`, and will provide a CLIP model output for subsequent nodes.

This node will detect models located in the `ComfyUI/models/text_encoders` folder,
 and it will also read models from additional paths configured in the extra_model_paths.yaml file.
 Sometimes, after adding models, you may need to **reload the ComfyUI interface** to allow it to read the model files in the corresponding folder.
