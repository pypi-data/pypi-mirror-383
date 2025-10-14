# KITECH Manufacturing Data Repository CLI & Library

KITECH 제조 데이터 리포지토리를 위한 Python 라이브러리 및 CLI 도구입니다.

## 기능

- 🔐 API Token 기반 인증
- 📦 Repository 목록 조회 및 관리
- 📁 파일/폴더 탐색 및 검색
- ⬇️ 단일/배치 파일 다운로드
- ⬆️ 파일 업로드
- 🚀 비동기 처리 지원
- 📊 진행률 표시

## 요구 사항

- Python 3.10 ~ 3.13
- uv (권장) 또는 pip

## 설치

### uv 사용 (권장)

```bash
# uv 설치 (아직 설치하지 않은 경우)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 프로젝트 설치
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .
```

### pip 사용

```bash
# 가상환경 생성
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 프로젝트 설치
pip install -e .
```

### 개발 환경 설정

```bash
# 개발 의존성 포함 설치
uv pip install -e ".[dev]"
# 또는
pip install -e ".[dev]"

# 코드 포맷팅
ruff format .

# 린팅
ruff check .

# 테스트 실행
pytest
pytest --cov  # 커버리지 포함
```

## CLI 사용법

### 1. 인증

```bash
# 로그인 (API Token 필요)
kitech auth login
# 또는 토큰 직접 제공
kitech auth login --token kt_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 로그아웃
kitech auth logout

# 인증 상태 확인
kitech auth status
```

### 2. Repository 조회

```bash
# Repository 목록 조회
kitech list repos

# 공유된 Repository 제외
kitech list repos --no-shared

# 페이지네이션
kitech list repos --page 1 --limit 10
```

### 3. 파일 목록 조회

```bash
# Repository의 파일 목록
kitech list files 123

# 특정 폴더 조회
kitech list files 123 --prefix data/

# 파일 검색
kitech list files 123 --search .csv
```

### 4. 다운로드

```bash
# 단일 파일 다운로드
kitech download file 123 --path /data/dataset.csv

# 폴더 다운로드
kitech download file 123 --path /data/models/

# 전체 Repository 다운로드
kitech download repo 123

# 배치 다운로드
kitech download batch 123 /data/file1.csv /data/file2.csv /models/

# 출력 디렉토리 지정
kitech download file 123 --path /data/dataset.csv --output ./downloads
```

### 5. 업로드

```bash
# 파일 업로드
kitech upload file 123 ./local_file.csv

# 특정 폴더에 업로드
kitech upload file 123 ./local_file.csv --path uploads/data/

# 디렉토리 전체 업로드
kitech upload directory 123 ./local_folder --path remote/path/
```

### 6. 기타

```bash
# 연결 테스트
kitech test

# 버전 확인
kitech version
```

## Library 사용법

```python
from kitech_repository import KitechClient

# 클라이언트 초기화
client = KitechClient(token="kt_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

# Repository 목록 조회
repos = client.list_repositories()
for repo in repos["repositories"]:
    print(f"{repo.id}: {repo.name}")

# 파일 목록 조회
files = client.list_files(repository_id=123, prefix="data/")
for file in files["files"]:
    if file.is_directory:
        print(f"📁 {file.name}/")
    else:
        print(f"📄 {file.name} ({file.size} bytes)")

# 파일 다운로드
downloaded_path = client.download_file(
    repository_id=123,
    path="/data/dataset.csv",
    output_dir=Path("./downloads")
)

# 파일 업로드
result = client.upload_file(
    repository_id=123,
    file_path=Path("./local_file.csv"),
    remote_path="uploads/"
)

# 배치 다운로드 (비동기)
import asyncio

async def batch_download():
    paths = ["/data/file1.csv", "/data/file2.csv"]
    files = await client.download_batch(
        repository_id=123,
        paths=paths
    )
    return files

downloaded_files = asyncio.run(batch_download())

# Context manager 사용
with KitechClient(token="kt_xxx") as client:
    repos = client.list_repositories()
    # 클라이언트 자동 종료
```

## API 문서

자세한 API 명세는 프로젝트 문서를 참고하세요:
- Base URL: `https://kitech-manufacturing-api.wimcorp.dev/v1`
- 인증: Bearer Token (`Authorization: Bearer kt_xxx`)

## 프로젝트 구조

```
kitech-repository-CLI/
├── kitech_repository/
│   ├── __init__.py
│   ├── lib/              # 라이브러리 핵심 모듈
│   │   ├── client.py     # API 클라이언트
│   │   ├── auth.py       # 인증 관리
│   │   ├── config.py     # 설정 관리
│   │   └── exceptions.py # 예외 정의
│   ├── models/           # 데이터 모델
│   │   ├── repository.py
│   │   ├── file.py
│   │   └── response.py
│   └── cli/              # CLI 명령어
│       ├── main.py
│       └── commands/
│           ├── auth.py
│           ├── list_cmd.py
│           ├── download.py
│           └── upload.py
├── tests/                # 테스트
│   ├── unit/
│   └── integration/
├── pyproject.toml        # 프로젝트 설정
├── .ruff.toml           # 코드 포맷터 설정
└── README.md
```

## 라이센스

TBD

## 기여

기여를 환영합니다! Pull Request를 보내주세요.