该节点会检测位于 `ComfyUI/models/controlnet` 文件夹下的模型，
同时也会读取你在 extra_model_paths.yaml 文件中配置的额外路径的模型，
有时你可能需要 **刷新 ComfyUI 界面** 才能让它读取到对应文件夹下的模型文件

控制网络加载节点旨在从指定路径加载一个ControlNet模型。它在初始化ControlNet模型中扮演着关键角色，这些模型对于在生成内容上应用控制机制或基于控制信号修改现有内容至关重要。

## 输入

| 参数名称 | 数据类型 | 作用 |
| --- | --- | --- |
| `ControlNet名称` | COMBO[STRING] | 指定要加载的ControlNet模型的名称。此名称用于在预定义的目录结构中定位模型文件。 |

## 输出

| 参数名称 | 数据类型 | 作用 |
| --- | --- | --- |
| `control_net` | CONTROL_NET | 返回加载的ControlNet模型，准备用于控制或修改内容生成过程。 |

---
