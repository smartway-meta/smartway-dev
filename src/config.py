import os
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import ChatOpenAI

# Load .env on import
load_dotenv(override=True)

def get_upstage_api_key() -> str:
    """Upstage API 키를 가져옵니다."""
    api_key = os.getenv("UPSTAGE_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("UPSTAGE_API_KEY is not set. Please set it in your .env file.")
    return api_key


def build_openai_client() -> OpenAI:
    """Upstage API를 사용하는 OpenAI 클라이언트를 생성합니다."""
    return OpenAI(api_key=get_upstage_api_key(), base_url="https://api.upstage.ai/v1")


def build_chat_model(temperature: float = 0.7, model: str = "solar-pro") -> ChatOpenAI:
    """
    Upstage Solar API를 사용하는 ChatOpenAI 모델을 생성합니다.
    
    Args:
        temperature: 모델의 temperature 설정 (0.0 ~ 1.0)
        model: 사용할 모델 이름 (기본값: solar-pro)
    
    Returns:
        ChatOpenAI: 설정된 Chat 모델
    """
    return ChatOpenAI(
        base_url="https://api.upstage.ai/v1/solar",
        api_key=get_upstage_api_key(),
        model=model,
        temperature=temperature
    )