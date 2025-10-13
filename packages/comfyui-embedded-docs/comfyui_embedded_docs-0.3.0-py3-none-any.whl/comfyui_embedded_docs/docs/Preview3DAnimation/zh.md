Preview3DAnimation节点主要用来预览3D模型素材输出，这个节点接收两个输入，一个是 Load3D 节点的 `camera_info` 以及 `模型文件` 的路径信息，模型路径输入要求位于 `ComfyUI/output` 文件夹

**支持格式**
目前该节点支持多种 3D 文件格式，包括 `.gltf`、`.glb`、`.obj`、`.fbx` 和 `.stl`。

**3D 节点预设**
3D 节点的一些相关偏好设置可以在 ComfyUI 的设置菜单中进行设置，请参考下面的文档了解对应的设置
[设置菜单](https://docs.comfy.org/zh-CN/interface/settings/3d)

## 输入

| 参数名称 | 数据类型        | 说明                                  |
| ------- | ------------- | ------------------------------------- |
| 相机信息 | LOAD3D_CAMERA | 相机信息                                |
| 模型文件 | STRING | 位于`ComfyUI/output/` 路径下的模型文件路径 |

## 模型画布(Canvas)区说明

目前 ComfyUI 前端中 3D 相关节点 Canvas 部分共用了 canvas 部分的组件，所以除了部分功能差异之外他们的基础功能操作都是一致的。

> 下面内容及界面在制作内容时以 Load3D 节点为主，实际节点界面及功能请参考实际节点界面

Canvas 区域包含了诸多的视图操作，包括：

- 预览视图设置（网格、背景色、预览视图）
- 相机控制: 控制FOV、相机类型
- 全局光照强度: 调节光照强度
- 模型导出: 支持`GLB`、`OBJ`、`STL` 格式
- 等

![Load 3D 节点UI](../Preview3D/asset/preview3d_canvas.jpg)

1. 包含了 Load 3D 节点的多个菜单以及隐藏菜单
2. 3D 视图操作轴

### 1. 视图操作

<video controls width="640" height="360">
  <source src="../Load3D/asset/view_operations.mp4" type="video/mp4">
  您的浏览器不支持视频播放。
</video>

视图控制操作：

- 鼠标左键点击 + 拖拽： 视图旋转控制
- 鼠标右键 + 拖拽： 平移视图
- 鼠标中键： 缩放控制
- 坐标轴： 切换视图

### 2. 左侧菜单功能

![Menu](../Load3D/asset/menu.webp)

在预览区域，有些视图操作相关的菜单被隐藏在了菜单里，点击菜单按钮可以展开对应不同的菜单

- 1. 场景（Scene）: 包含预览窗口网格、背景色、缩略图设置
- 2. 模型（Model）: 模型渲染模式、纹理材质、上方向设置
- 3. 摄像机（Camera）: 轴测视图和透视视图切换、透视视角大小设置
- 4. 灯光（Light）: 场景全局光照强度
- 5. 导出（Export）: 导出模型为其它格式（GLB、OBJ、STL）

#### 场景（Scene）

![scene menu](../Load3D/asset/menu_scene.webp)

场景菜单提供了对场景的一些基础设置功能

1. 显示 / 隐藏网格
2. 设置背景色
3. 点击上传设置背景图片
4. 隐藏缩略预览图

#### 模型(Model)

![Menu_Scene](../Load3D/asset/menu_model.webp)

模型菜单提供了一些模型的相关功能

1. **上方向(Up direction)**: 确定模型的哪个轴为上方向
2. **渲染模式（Material mode）**: 模型渲染模式切换 原始（Original）、法线(Normal)、线框(Wireframe)、线稿(Lineart)

#### 摄像机（Camera）

![menu_modelmenu_camera](../Load3D/asset/menu_camera.webp)

该菜单提供了轴测视图和透视视图切换、透视视角大小设置

1. **相机（Camera）**: 在轴测视图和正交视图之间快速切换
2. **视场角(FOV)**: 调整 FOV 视角角度

#### 灯光（Light）

![menu_modelmenu_camera](../Load3D/asset/menu_light.webp)

通过该菜单可以快速调节模型场景的全局光照强度

#### 导出（Export）

![menu_export](../Load3D/asset/menu_export.webp)

该菜单提供了一个快速转换模型格式并导出的能力
