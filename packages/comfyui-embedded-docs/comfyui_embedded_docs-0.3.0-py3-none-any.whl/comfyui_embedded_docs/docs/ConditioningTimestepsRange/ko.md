> 이 문서는 AI에 의해 생성되었습니다. 오류를 발견하거나 개선 제안이 있으시면 기여해 주세요! [GitHub에서 편집](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ConditioningTimestepsRange/ko.md)

ConditioningTimestepsRange 노드는 생성 과정에서 컨디셔닝 효과가 적용되는 시점을 제어하기 위해 세 가지 구별된 타임스텝 범위를 생성합니다. 시작 및 종료 백분율 값을 입력받아 전체 타임스텝 범위(0.0에서 1.0까지)를 세 개의 세그먼트로 나눕니다: 지정된 백분율 사이의 주 범위, 시작 백분율 이전의 범위, 그리고 종료 백분율 이후의 범위입니다.

## 입력

| 매개변수 | 데이터 타입 | 필수 | 범위 | 설명 |
|-----------|-----------|----------|-------|-------------|
| `시작 퍼센트` | FLOAT | 예 | 0.0 - 1.0 | 타임스텝 범위의 시작 백분율 (기본값: 0.0) |
| `종료 퍼센트` | FLOAT | 예 | 0.0 - 1.0 | 타임스텝 범위의 종료 백분율 (기본값: 1.0) |

## 출력

| 출력 이름 | 데이터 타입 | 설명 |
|-------------|-----------|-------------|
| `이전 범위` | TIMESTEPS_RANGE | start_percent와 end_percent로 정의된 주 타임스텝 범위 |
| `이후 범위` | TIMESTEPS_RANGE | 0.0부터 start_percent까지의 타임스텝 범위 |
| `AFTER_RANGE` | TIMESTEPS_RANGE | end_percent부터 1.0까지의 타임스텝 범위 |
