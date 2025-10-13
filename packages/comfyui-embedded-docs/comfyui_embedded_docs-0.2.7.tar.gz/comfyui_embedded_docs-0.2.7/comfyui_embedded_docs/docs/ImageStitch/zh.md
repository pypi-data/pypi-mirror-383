这个节点可以将两张图片按指定方向（上、下、左、右）拼接在一起，支持调整图片大小匹配和添加间隔。

## 输入

| 参数名称 | 数据类型 | 输入方式 | 默认值 | 取值范围 | 功能说明 |
|----------|----------|----------|---------|----------|----------|
| `image1` | IMAGE | 必填 | - | - | 第一张要拼接的图片 |
| `image2` | IMAGE | 选填 | None | - | 第二张要拼接的图片，如果不提供则只返回第一张图片 |
| `direction` | STRING | 必填 | right | right/down/left/up | 第二张图片的拼接方向：right(右)、down(下)、left(左)、up(上) |
| `match_image_size` | BOOLEAN | 必填 | True | True/False | 是否调整第二张图片的大小以匹配第一张图片的尺寸 |
| `spacing_width` | INT | 必填 | 0 | 0-1024 | 两张图片之间的间隔宽度，必须是偶数 |
| `spacing_color` | STRING | 必填 | white | white/black/red/green/blue | 拼接图片之间间隔的颜色 |

> 对于 `spacing_color` 除了 "white/black" 之外，如果 `match_image_size` 设置为 `false` 那么空白部分将使用黑色作为填充色

## 输出

| 输出名称 | 数据类型 | 说明 |
|----------|----------|------|
| `IMAGE` | IMAGE | 拼接后的图片 |

## 工作流示例

在下面的工作流中，我们使用了3 张不同尺寸的输入图片作为示例

- image1: 500x300
- image2: 400x250
- image3: 300x300

![workflow](./asset/workflow.webp)

**第一个 Image Stitch 节点**

- `match_image_size`: false, 两张图像将会已原有尺寸拼接
- `direction`: up, `image2` 将会在 `image1` 上方
- `spacing_width`: 20
- `spacing_color` : black

输出图片1:

![output1](./asset/output-1.webp)

**第二个 Image Stitch 节点**

- `match_image_size`: true, 第二张图像将会缩放到与第一张图像相同的高度或者宽度
- `direction`:right, `image3` 将会出现在右侧
- `spacing_width`: 20
- `spacing_color` : white

输出图片2:

![output2](./asset/output-2.webp)
