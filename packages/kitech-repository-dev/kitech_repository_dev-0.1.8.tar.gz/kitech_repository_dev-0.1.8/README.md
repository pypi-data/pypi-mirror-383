# KITECH Manufacturing Data Repository CLI

KITECH 제조 데이터 리포지토리를 위한 Python CLI 도구입니다.

## 기능

- 🖥️ **대화형 파일 관리자 (TUI)** - 듀얼 패널 UI로 직관적인 파일 관리
- 🔐 API Token 기반 인증
- ⬇️ 파일/폴더 다운로드 (MD5 무결성 검증)
- ⬆️ 파일/폴더 업로드 (MD5 무결성 검증)
- 📊 실시간 진행률 표시

## 요구 사항

- Python 3.10 ~ 3.13
- pip

## 설치

```bash
pip install kitech-repository-dev
```

## 사용법

### 🚀 대화형 파일 관리자

```bash
# 파일 관리자 실행
kitech-dev manager start

# 키보드 단축키
# Tab       - 패널 간 이동
# ↑/↓       - 파일 선택
# Enter     - 폴더 열기/파일 선택
# F3        - 다운로드
# F5        - 업로드
# F10/ESC   - 종료
```

<!--
### 인증

```bash
# API Token으로 로그인
kitech-dev auth login

# 로그아웃
kitech-dev auth logout
```

### 기타 CLI 명령어

```bash
# 연결 테스트
kitech-dev test

# Repository 목록 조회
kitech-dev list repos

# 파일 목록 조회
kitech-dev list files <repository_id>

# 파일 다운로드
kitech-dev download file <repository_id> --path /path/to/file

# 파일 업로드
kitech-dev upload file <repository_id> <local_file>
```
-->

## 환경 설정

API 서버 주소를 설정해야 합니다:

```bash
# 환경 변수로 설정
export KITECH_API_BASE_URL=https://your-api-server.com

# 또는 .env 파일에 작성
echo "KITECH_API_BASE_URL=https://your-api-server.com" > .env
```

**주의**: `/v1`은 자동으로 추가되므로 입력하지 마세요.

---

## 개발자를 위한 Library API

Python 프로그램에서 직접 사용할 수 있습니다:

```python
from kitech_repository import KitechClient

client = KitechClient(token="kt_xxx")
repos = client.list_repositories()
client.download_file(repository_id=123, path="/data/file.csv")
client.upload_file(repository_id=123, file_path="local.csv")
```

## 라이센스

TBD