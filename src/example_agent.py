"""
LangGraph Agent 예제
도구를 사용하는 Agent를 구현한 예제입니다.
"""

from typing import TypedDict, Annotated, Literal

from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from config import build_chat_model


# 도구 정의
@tool
def multiply(a: int, b: int) -> int:
    """두 숫자를 곱합니다."""
    return a * b


@tool
def add(a: int, b: int) -> int:
    """두 숫자를 더합니다."""
    return a + b


@tool
def divide(a: int, b: int) -> float:
    """두 숫자를 나눕니다."""
    if b == 0:
        return "0으로 나눌 수 없습니다."
    return a / b


# State 정의
class State(TypedDict):
    messages: Annotated[list, add_messages]


# 도구 리스트
tools = [multiply, add, divide]
tool_node = ToolNode(tools)


def chatbot(state: State):
    """Agent 노드 - Upstage Solar-Pro를 호출하여 응답을 생성하거나 도구를 호출합니다."""
    llm = build_chat_model(temperature=0.7)
    llm_with_tools = llm.bind_tools(tools)
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


def route_tools(state: State) -> Literal["tools", "__end__"]:
    """
    조건부 엣지 - 도구 호출이 필요한지 판단합니다.
    마지막 메시지에 tool_calls가 있으면 "tools"로, 없으면 종료합니다.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return "__end__"


def create_agent_graph():
    """Agent 그래프를 생성합니다."""
    graph_builder = StateGraph(State)
    
    # 노드 추가
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", tool_node)
    
    # 엣지 추가
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges("chatbot", route_tools, {"tools": "tools", "__end__": END})
    graph_builder.add_edge("tools", "chatbot")
    
    # 그래프 컴파일
    graph = graph_builder.compile()
    return graph


def main():
    """메인 함수"""
    # 그래프 생성
    graph = create_agent_graph()
    
    # 테스트 실행
    print("LangGraph Agent 예제 (계산기)")
    print("-" * 50)
    
    # 사용자 메시지로 그래프 실행
    test_queries = [
        "15와 7을 곱해주세요.",
        "100을 4로 나눈 다음, 그 결과에 3을 더해주세요."
    ]
    
    for query in test_queries:
        print(f"\nUser: {query}")
        response = graph.invoke({
            "messages": [("user", query)]
        })
        print(f"Assistant: {response['messages'][-1].content}")


if __name__ == "__main__":
    main()
