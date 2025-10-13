> このドキュメントは AI によって生成されました。エラーを見つけた場合や改善のご提案がある場合は、ぜひ貢献してください！ [GitHub で編集](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/KlingCameraControlT2VNode/ja.md)

# Kling Text to Video Camera Control ノード

Kling Text to Video Camera Control ノードは、テキストを映画のようなビデオに変換し、実際の映画撮影を模倣したプロフェッショナルなカメラ動作を実現します。このノードは、元のテキストに焦点を当てたまま、ズーム、回転、パン、チルト、一人称視点などの仮想カメラアクションを制御することをサポートします。カメラ制御はプロモードでのみサポートされており、kling-v1-5モデルで5秒間の動画生成に限定されているため、動画の長さ、モード、モデル名は固定されています。

## 入力パラメータ

| パラメータ名 | データ型 | 必須 | 範囲 | 説明 |
|-----------|-----------|----------|-------|-------------|
| `prompt` | STRING | はい | - | 肯定的なテキストプロンプト |
| `negative_prompt` | STRING | はい | - | 否定的なテキストプロンプト |
| `cfg_scale` | FLOAT | いいえ | 0.0-1.0 | 出力がプロンプトにどれだけ忠実に従うかを制御します（デフォルト: 0.75） |
| `aspect_ratio` | COMBO | いいえ | "16:9"<br>"9:16"<br>"1:1"<br>"21:9"<br>"3:4"<br>"4:3" | 生成されるビデオのアスペクト比（デフォルト: "16:9"） |
| `camera_control` | CAMERA_CONTROL | いいえ | - | Kling Camera Controls ノードを使用して作成できます。ビデオ生成中のカメラの動きとモーションを制御します。 |

## 出力

| 出力名 | データ型 | 説明 |
|-------------|-----------|-------------|
| `video_id` | VIDEO | カメラ制御効果が適用された生成ビデオ |
| `duration` | STRING | 生成されたビデオの一意の識別子 |
| `duration` | STRING | 生成されたビデオの再生時間 |
