# DriverMakery

PDF에서 텍스트를 뽑아 레지스터 이름(예: `DENALI_*_##`) 기준으로 파트를 나누고,
Gemini API로 JSON을 받아 C 헤더를 생성하는 간단한 파이프라인.

## 설치
```bash
pip install -e .
```

## 설정
- `.env` 또는 `config.{toml|yaml|json}`를 사용
- 예시는 `config.example.*` 및 `.env.example` 참고

## 사용
```bash
drivermakery prepare
drivermakery split
drivermakery build
drivermakery build 3,5-7,10
drivermakery clean
```
