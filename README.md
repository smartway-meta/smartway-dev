# SmartWay Dev - LangGraph 프로젝트

LangGraph를 활용한 AI Agent 개발 프로젝트입니다.

## 🚀 시작하기

### 1. 환경 설정

```bash
# 가상환경 활성화
source venv/bin/activate

# 패키지 설치 (이미 설치됨)
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성하고, API 키를 입력하세요.

```bash
cp .env.example .env
```

`.env` 파일에서 다음 항목을 설정하세요:
- `UPSTAGE_API_KEY`: Upstage API 키 (필수) - [Upstage Console](https://console.upstage.ai/)에서 발급
- `LANGCHAIN_API_KEY`: LangSmith API 키 (선택사항, 디버깅용)

### 3. 예제 실행

#### 기본 챗봇 예제
```bash
python src/example_basic.py
```

#### Agent 예제 (도구 사용)
```bash
python src/example_agent.py
```

## 📁 프로젝트 구조

```
smartway-dev/
├── venv/                 # Python 가상환경
├── src/                  # 소스 코드
│   ├── config.py         # API 클라이언트 설정 (중앙 관리)
│   ├── example_basic.py  # 기본 챗봇 예제
│   └── example_agent.py  # Agent 예제
├── graphs/               # 그래프 정의
├── utils/                # 유틸리티 함수
├── .env                  # 환경 변수 (gitignore)
├── .env.example          # 환경 변수 예제
├── .gitignore
├── requirements.txt      # 패키지 목록
└── README.md
```

## 🛠️ 설치된 패키지

- **langgraph**: 상태 기반 멀티 액터 애플리케이션 구축 프레임워크
- **langchain**: LLM 애플리케이션 개발 프레임워크
- **langchain-openai**: OpenAI 호환 API 통합 (Upstage Solar-Pro 사용)
- **langchain-community**: 커뮤니티 통합
- **python-dotenv**: 환경 변수 관리

### ℹ️ Upstage Solar API 사용 방법

이 프로젝트는 `config.py`를 통해 Upstage Solar-Pro 모델을 중앙에서 관리합니다:

```python
from config import build_chat_model

# 간단하게 모델 사용
llm = build_chat_model(temperature=0.7)

# 또는 사용자 정의 설정
llm = build_chat_model(temperature=0.5, model="solar-pro")
```

**`config.py`의 장점:**
- ✅ API 키 관리 중앙화
- ✅ 모델 설정 일관성 유지
- ✅ 코드 재사용성 향상
- ✅ 환경 변수 자동 검증

## 📚 주요 개념

### LangGraph란?

LangGraph는 LangChain을 기반으로 구축된 라이브러리로, 상태가 있는(stateful) 멀티 액터 애플리케이션을 만들 수 있게 해줍니다. 주요 특징:

- **노드(Nodes)**: 작업을 수행하는 함수
- **엣지(Edges)**: 노드 간의 연결
- **상태(State)**: 그래프 실행 중 유지되는 데이터
- **조건부 엣지**: 상태에 따라 다른 노드로 이동

### 기본 워크플로우

1. **State 정의**: 그래프에서 사용할 데이터 구조 정의
2. **노드 생성**: 각 작업을 수행하는 함수 작성
3. **그래프 구축**: 노드와 엣지를 추가하여 워크플로우 구성
4. **그래프 컴파일**: 실행 가능한 그래프로 컴파일
5. **실행**: 입력 데이터로 그래프 실행

## 🔧 다음 단계

1. [Upstage Console](https://console.upstage.ai/)에서 API 키 발급
2. `.env` 파일에 `UPSTAGE_API_KEY` 설정
3. 예제 코드 실행해보기
4. 필요에 따라 커스텀 노드와 그래프 작성
5. `graphs/` 디렉토리에 프로젝트별 그래프 구현

## 📖 참고 자료

- [Upstage Solar API](https://developers.upstage.ai/) - Solar-Pro 모델 문서
- [LangGraph 공식 문서](https://langchain-ai.github.io/langgraph/)
- [LangChain 공식 문서](https://python.langchain.com/)
- [LangSmith](https://smith.langchain.com/) - 디버깅 및 모니터링

## 🤝 기여

이슈나 PR은 언제나 환영합니다!

## 📝 라이센스

MIT License
