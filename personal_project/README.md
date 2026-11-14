# 충돌 회피 알고리즘 비교 (APF · Bug2 · DWA)

2차원 평면에서 이동체가 장애물을 피해 목적지에 도달하는 세 방식(인공 포텐셜 필드,
Bug2, 동적 창 접근법)을 같은 조건에서 비교한다. 계획은 [ROADMAP.md](ROADMAP.md),
작업 규칙은 [project_guidelines.md](project_guidelines.md)에 있다.

> 진행 중이다. 아래 내용은 지금까지 구현한 부분(지도 생성, 시뮬레이터, APF, Bug2, DWA)만 다룬다.
> 알고리즘 구현과 본 실험은 단계가 끝날 때마다 이 문서에 추가한다.

## 환경

- Python 3.13에서 확인했다. 지금까지의 코드는 표준 라이브러리만 쓴다.
- 모든 명령은 `personal_project/` 폴더에서 실행한다.

```bash
cd personal_project
```

## 구성

```plaintext
src/mapgen.py          시드 기반 랜덤 지도 생성 + 풀이 가능성 검사
src/sim.py             시뮬레이터 (이동체, 충돌 판정, 실행 루프)
src/algo_straight.py   직진 더미 알고리즘 (시뮬레이터 검증용)
src/algo_apf.py        인공 포텐셜 필드 (APF)
src/tune_apf.py        APF 파라미터 탐색 (튜닝 시드만 사용)
src/algo_bug2.py       Bug2 (연속 공간)
src/tune_bug2.py       Bug2 파라미터 탐색 (튜닝 시드만 사용)
src/algo_dwa.py        동적 창 접근법 (DWA)
src/tune_dwa.py        DWA 파라미터 탐색 (튜닝 시드만 사용, 병렬)
src/check_straight.py  직진 더미를 평가 시드에서 돌려 보는 점검 스크립트
tests/test_sim.py      시뮬레이터 단위 테스트
tests/test_apf.py      APF 단위 테스트
tests/test_bug2.py     Bug2 단위 테스트
tests/test_dwa.py      DWA 단위 테스트
```

## 실행

### 1. 테스트

```bash
python -m unittest discover -s tests -v
```

26개 테스트가 모두 `ok`여야 한다. 수 초 걸린다.

### 2. 지도 생성 확인

```bash
python src/mapgen.py
```

평가 시드(1000~1299)로 유형별 지도를 만들고, 채택·거부된 지도 수와 평균 장애물 수를
출력한다. 약 40초 걸린다. 같은 시드는 항상 같은 지도를 만든다.

### 3. 시뮬레이터 점검 (직진 더미)

```bash
python src/check_straight.py
```

장애물을 무시하고 직진하는 알고리즘을 평가 지도에서 돌려 도착·충돌 수를 출력한다.
약 40초 걸린다. 장애물이 많을수록 충돌이 늘어나는지 보면 시뮬레이터가 맞게
동작하는지 확인할 수 있다.

### 4. APF 파라미터 탐색

```bash
python src/tune_apf.py
```

튜닝 시드(0~49) 147개 지도에서 `k_rep` 6가지 × `d0` 4가지를 돌려 설정마다 도착·충돌·
타임아웃 수를 출력한다. 수 분 걸린다. 마지막 줄의 `best`가 확정값 선택 근거다.
확정값은 `src/algo_apf.py`의 `K_REP`, `D0`에 적혀 있다(`K_REP=2.5`, `D0=12`). 평가 시드는
쓰지 않는다.

### 5. Bug2 파라미터 탐색

```bash
python src/tune_bug2.py
```

튜닝 시드 147개 지도에서 `hit_dist` × `follow_dist` × `leave_tol` 27가지를 돌려 설정마다
도착·충돌·타임아웃 수를 출력한다. 수 분 걸린다. 확정값은 `src/algo_bug2.py`의
`HIT_DIST`, `FOLLOW_DIST`, `LEAVE_TOL`에 적혀 있다(2.0 / 1.0 / 2.0). 평가 시드는 쓰지 않는다.

### 6. DWA 파라미터 탐색

```bash
python src/tune_dwa.py
```

튜닝 시드 147개 지도에서 `beta` × `gamma` × `t_pred` 12가지를 돌려 설정마다 도착·충돌·
타임아웃 수를 출력한다. 워커 프로세스 4개로 병렬 실행하며(`src/tune_dwa.py`의 `WORKERS`),
**1시간 안팎 걸린다** (우리 환경에서 약 64분). 끝나야 결과가 한꺼번에 출력된다. 확정값은
`src/algo_dwa.py`의 `BETA`, `GAMMA`, `T_PRED`에 적혀 있다(1.0 / 2.0 / 1.5). 평가 시드는 쓰지 않는다.

## 설정값

| 항목 | 값 | 위치 |
|---|---|---|
| 지도 크기 | 100 × 100 | `mapgen.py` |
| 시작점 → 목표점 | (5, 5) → (95, 95) | `mapgen.py` |
| 이동체 반지름 / 여유 거리 | 1.0 / 0.5 | `mapgen.py` |
| 튜닝 시드 / 평가 시드 | 0~49 / 1000~1299 | `mapgen.py` |
| 시간 간격 / 최대 속도 / 최대 회전 속도 | 0.1 s / 2.0 / 2.0 rad/s | `sim.py` |
| 센서 범위 / 도착 허용 거리 / 최대 스텝 | 15 / 1.5 / 3000 | `sim.py` |
| 지도 경계 | 센서에 가상 원으로 보임 (반지름 2, 간격 1.5, 안쪽 0.15), 나가면 충돌 | `sim.py` |
| APF `k_rep` / `d0` | 2.5 / 12.0 (튜닝 시드에서 확정) | `algo_apf.py` |
| Bug2 `hit_dist` / `follow_dist` / `leave_tol` | 2.0 / 1.0 / 2.0 (튜닝 시드에서 확정) | `algo_bug2.py` |
| DWA `beta` / `gamma` / `t_pred` | 1.0 / 2.0 / 1.5 (튜닝 시드에서 확정) | `algo_dwa.py` |
