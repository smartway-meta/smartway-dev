"""
LangGraph 기본 예제
간단한 챗봇 그래프를 구현한 예제입니다.
"""

# ============================================================
# 1. 필요한 라이브러리 임포트
# ============================================================
from typing import TypedDict, Annotated  # 타입 힌팅을 위한 모듈

from langgraph.graph import StateGraph, START, END  # LangGraph 그래프 구성 요소
from langgraph.graph.message import add_messages  # 메시지 추가 헬퍼 함수
from config import build_chat_model  # Upstage API 클라이언트 생성 함수


# ============================================================
# 2. State(상태) 클래스 정의
# ============================================================
class State(TypedDict):
    """
    그래프 실행 중 유지되는 상태를 정의하는 클래스
    - messages: 대화 메시지 리스트 (사용자 메시지, AI 응답 등)
    - Annotated[list, add_messages]: 메시지가 자동으로 누적되도록 설정
    """
    messages: Annotated[list, add_messages]


# ============================================================
# 3. 노드(Node) 함수 정의
# ============================================================
def chatbot(state: State):
    """
    챗봇 노드 - Upstage Solar-Pro를 호출하여 응답을 생성합니다.
    
    Args:
        state (State): 현재 그래프의 상태 (메시지 리스트 포함)
    
    Returns:
        dict: 업데이트할 상태 {"messages": [AI 응답 메시지]}
    
    동작 과정:
    1. build_chat_model()로 LLM 인스턴스 생성
    2. state["messages"]를 LLM에 전달하여 응답 생성
    3. 생성된 응답을 messages 리스트에 추가
    """
    llm = build_chat_model(temperature=0.7)  # temperature: 응답의 창의성 조절 (0~1)
    return {"messages": [llm.invoke(state["messages"])]}  # LLM 호출 및 응답 반환


def get_node_edge_data(state: State):
    return

def find_highlight_edge(state: State):
    return

def highlighting_edge(state: State):
    return

# ============================================================
# 4. 그래프 생성 함수
# ============================================================
def create_graph():
    """
    LangGraph 그래프를 생성하고 설정합니다.
    
    Returns:
        CompiledGraph: 실행 가능한 컴파일된 그래프
    
    그래프 구조:
        START → chatbot → END
    
    동작 흐름:
    1. StateGraph(State)로 그래프 빌더 생성
    2. "chatbot" 노드 추가 (위에서 정의한 chatbot 함수 사용)
    3. START에서 chatbot으로 가는 엣지(화살표) 추가
    4. chatbot에서 END로 가는 엣지 추가
    5. compile()로 그래프를 실행 가능한 형태로 컴파일
    """
    graph_builder = StateGraph(State)  # State 타입을 사용하는 그래프 빌더 생성
    
    # 노드 추가: "chatbot"이라는 이름으로 chatbot 함수를 노드로 등록
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("get_node_edge_data", get_node_edge_data)
    graph_builder.add_node("find_highlight_edge", find_highlight_edge)
    graph_builder.add_node("highlighting_edge", highlighting_edge)
    # 엣지 추가: START(시작점) → chatbot 노드로 연결
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", "get_node_edge_data")
    graph_builder.add_edge("get_node_edge_data", "find_highlight_edge")
    graph_builder.add_edge("find_highlight_edge", "highlighting_edge")
    graph_builder.add_edge("highlighting_edge", END)
    
    # 그래프 컴파일: 실행 가능한 그래프 객체로 변환
    graph = graph_builder.compile()
    return graph


# ============================================================
# 5. 메인 함수 (실제 실행 로직)
# ============================================================
def main():
    """
    메인 함수 - 그래프를 생성하고 실행합니다.
    
    실행 순서:
    1. create_graph()로 그래프 생성
    2. 사용자로부터 질문 입력 받기
    3. graph.invoke()로 그래프 실행
    4. 결과 출력
    """
    # 1. 그래프 생성
    graph = create_graph()
    
    # 2. 프로그램 시작 메시지 출력
    print("=" * 60)
    print("🤖 LangGraph 챗봇 예제 - Find Highlight")
    print("=" * 60)
    print("종료하려면 'quit', 'exit', 'q' 중 하나를 입력하세요.")
    print("-" * 60)
    
    # 3. 대화 루프 시작
    while True:
        # 사용자로부터 질문 입력 받기
        user_input = input("\n💬 User: ").strip()
        
        # 종료 명령어 체크
        if user_input.lower() in ['quit', 'exit', 'q', '종료']:
            print("\n👋 챗봇을 종료합니다. 감사합니다!")
            break
        
        # 빈 입력 체크
        if not user_input:
            print("⚠️  질문을 입력해주세요.")
            continue
        
        # 4. 사용자 메시지로 그래프 실행
        # invoke() 메서드에 사용자 입력을 상태로 전달
        # {"messages": [("user", 사용자입력)]} 형태로 전달
        try:
            print("\n🤔 생각 중...\n")
            
            response = graph.invoke({
                "messages": [("user", user_input)]
            })
            # 실행 흐름:
            # a) START → chatbot 노드로 이동
            # b) chatbot 함수 실행: LLM이 응답 생성
            # c) chatbot → get_node_edge_data 노드로 이동
            # d) find_highlight_edge → highlighting_edge → END
            # e) 최종 상태(response) 반환
            
            # 5. AI 응답 출력
            # response['messages'][-1]: 메시지 리스트의 마지막 요소 (AI 응답)
            # .content: 메시지 객체의 실제 텍스트 내용
            print(f"🤖 Assistant: {response['messages'][-1].content}")
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\n\n👋 프로그램을 중단합니다.")
            break
        except Exception as e:
            print(f"\n❌ 오류가 발생했습니다: {e}")
            print("다시 시도해주세요.")
            continue


# ============================================================
# 6. 스크립트 진입점 (Entry Point)
# ============================================================
if __name__ == "__main__":
    """
    이 블록이 실행 시작점입니다!
    
    - python src/example_basic.py 명령으로 실행하면
    - Python 인터프리터가 이 블록을 가장 먼저 실행합니다
    - __name__ == "__main__"은 "이 파일이 직접 실행되었는가?"를 체크
    - 다른 파일에서 import될 때는 이 블록이 실행되지 않음
    
    실행 순서:
    1. Python이 파일을 위에서 아래로 읽으며 함수들을 메모리에 로드
    2. if __name__ == "__main__": 블록에 도달
    3. main() 함수 호출
    4. main() 내부에서 create_graph() → graph.invoke() 순서로 실행
    """
    main()  # 메인 함수 호출 - 여기서부터 실제 실행이 시작됩니다!
