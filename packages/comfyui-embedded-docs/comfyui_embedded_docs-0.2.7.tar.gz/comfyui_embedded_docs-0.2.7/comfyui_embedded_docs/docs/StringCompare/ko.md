> 이 문서는 AI에 의해 생성되었습니다. 오류를 발견하거나 개선 제안이 있으시면 기여해 주세요! [GitHub에서 편집](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StringCompare/ko.md)

StringCompare 노드는 두 개의 텍스트 문자열을 다양한 비교 방법을 사용하여 비교합니다. 한 문자열이 다른 문자열로 시작하는지, 끝나는지, 또는 두 문자열이 정확히 동일한지 확인할 수 있습니다. 비교는 대소문자 차이를 고려하거나 고려하지 않고 수행할 수 있습니다.

## 입력

| 매개변수 | 데이터 타입 | 필수 | 범위 | 설명 |
|-----------|-----------|----------|-------|-------------|
| `string_a` | STRING | 예 | - | 비교할 첫 번째 문자열 |
| `string_b` | STRING | 예 | - | 비교 대상이 되는 두 번째 문자열 |
| `mode` | COMBO | 예 | "Starts With"<br>"Ends With"<br>"Equal" | 사용할 비교 방법 |
| `case_sensitive` | BOOLEAN | 아니오 | - | 비교 시 대소문자를 고려할지 여부 (기본값: true) |

## 출력

| 출력 이름 | 데이터 타입 | 설명 |
|-------------|-----------|-------------|
| `output` | BOOLEAN | 비교 조건이 충족되면 true를 반환하고, 그렇지 않으면 false를 반환합니다 |
