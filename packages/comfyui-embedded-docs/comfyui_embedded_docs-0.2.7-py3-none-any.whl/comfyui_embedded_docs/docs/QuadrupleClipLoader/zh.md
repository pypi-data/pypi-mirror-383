四重 CLIP 加载器 QuadrupleCLIPLoader 是 ComfyUI 的核心节点之一，最先添加在针对 HiDream I1 版本的模型支持上，如果你发现这个节点缺失，试着更新ComfyUI 版本到最新版本以保证节点支持。

它需要 4 个 CLIP 模型，分别对应 `clip_name1`, `clip_name2`, `clip_name3`, `clip_name4` 这四个参数，并会提供一个 CLIP 模型输出用于后续节点使用。

该节点会检测位于 `ComfyUI/models/text_encoders` 文件夹下的模型，
同时也会读取你在 extra_model_paths.yaml 文件中配置的额外路径的模型，
有时添加模型后你可能需要 **重载 ComfyUI 界面** 才能让它读取到对应文件夹下的模型文件
