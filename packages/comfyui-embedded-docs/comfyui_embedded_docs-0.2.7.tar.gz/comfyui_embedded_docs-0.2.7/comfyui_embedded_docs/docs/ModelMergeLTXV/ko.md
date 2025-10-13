> 이 문서는 AI에 의해 생성되었습니다. 오류를 발견하거나 개선 제안이 있으시면 기여해 주세요! [GitHub에서 편집](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeLTXV/ko.md)

ModelMergeLTXV 노드는 LTXV 모델 아키텍처에 특화된 고급 모델 병합 작업을 수행합니다. 트랜스포머 블록, 프로젝션 레이어 및 기타 특수화된 모듈을 포함한 다양한 모델 구성 요소에 대한 보간 가중치를 조정하여 두 개의 서로 다른 모델을 혼합할 수 있습니다.

## 입력

| 매개변수 | 데이터 타입 | 필수 | 범위 | 설명 |
|-----------|-----------|----------|-------|-------------|
| `모델1` | MODEL | 예 | - | 병합할 첫 번째 모델 |
| `모델2` | MODEL | 예 | - | 병합할 두 번째 모델 |
| `patchify_proj.` | FLOAT | 예 | 0.0 - 1.0 | 패치화 프로젝션 레이어에 대한 보간 가중치 (기본값: 1.0) |
| `adaln_single.` | FLOAT | 예 | 0.0 - 1.0 | 적응형 레이어 정규화 단일 레이어에 대한 보간 가중치 (기본값: 1.0) |
| `caption_projection.` | FLOAT | 예 | 0.0 - 1.0 | 캡션 프로젝션 레이어에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.0.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 0에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.1.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 1에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.2.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 2에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.3.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 3에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.4.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 4에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.5.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 5에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.6.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 6에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.7.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 7에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.8.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 8에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.9.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 9에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.10.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 10에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.11.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 11에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.12.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 12에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.13.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 13에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.14.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 14에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.15.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 15에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.16.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 16에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.17.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 17에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.18.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 18에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.19.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 19에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.20.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 20에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.21.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 21에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.22.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 22에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.23.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 23에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.24.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 24에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.25.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 25에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.26.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 26에 대한 보간 가중치 (기본값: 1.0) |
| `transformer_blocks.27.` | FLOAT | 예 | 0.0 - 1.0 | 트랜스포머 블록 27에 대한 보간 가중치 (기본값: 1.0) |
| `scale_shift_table` | FLOAT | 예 | 0.0 - 1.0 | 스케일 시프트 테이블에 대한 보간 가중치 (기본값: 1.0) |
| `proj_out.` | FLOAT | 예 | 0.0 - 1.0 | 프로젝션 출력 레이어에 대한 보간 가중치 (기본값: 1.0) |

## 출력

| 출력 이름 | 데이터 타입 | 설명 |
|-------------|-----------|-------------|
| `model` | MODEL | 지정된 보간 가중치에 따라 두 입력 모델의 특징을 결합한 병합된 모델 |
