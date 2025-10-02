"""
LangGraph 기본 예제
간단한 챗봇 그래프를 구현한 예제입니다.
"""

from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from config import build_chat_model

# State 정의
class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    """챗봇 노드 - Upstage Solar-Pro를 호출하여 응답을 생성합니다."""
    llm = build_chat_model(temperature=0.7)
    return {"messages": [llm.invoke(state["messages"])]}


# 그래프 구성
def create_graph():
    """LangGraph 그래프를 생성합니다."""
    graph_builder = StateGraph(State)
    
    # 노드 추가
    graph_builder.add_node("chatbot", chatbot)
    
    # 엣지 추가
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    
    # 그래프 컴파일
    graph = graph_builder.compile()
    return graph


def main():
    """메인 함수"""
    # 그래프 생성
    graph = create_graph()
    
    # 테스트 실행
    print("LangGraph 챗봇 예제")
    print("-" * 50)
    
    # 사용자 메시지로 그래프 실행
    response = graph.invoke({
        "messages": [("user", "안녕하세요! LangGraph에 대해 간단히 설명해주세요.")]
    })
    
    # 응답 출력
    print(f"User: 안녕하세요! LangGraph에 대해 간단히 설명해주세요.")
    print(f"Assistant: {response['messages'][-1].content}")


if __name__ == "__main__":
    main()
