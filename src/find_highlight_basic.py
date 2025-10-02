"""
LangGraph 기본 예제
간단한 챗봇 그래프를 구현한 예제입니다.
"""

# ============================================================
# 1. 필요한 라이브러리 임포트
# ============================================================
import json  # JSON 파일 처리를 위한 모듈
import os  # 파일 경로 처리를 위한 모듈
from typing import TypedDict, Annotated, Optional  # 타입 힌팅을 위한 모듈

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
    - graph_data: ReactFlow 그래프 데이터 (노드와 엣지 정보)
    - Annotated[list, add_messages]: 메시지가 자동으로 누적되도록 설정
    """
    messages: Annotated[list, add_messages]
    graph_data: Optional[dict]  # ReactFlow 그래프 데이터 저장


# ============================================================
# 3. 노드(Node) 함수 정의
# ============================================================
def select_edge(state: State):
    """
    챗봇 노드 - Upstage Solar-Pro를 호출하여 응답을 생성합니다.
    
    Args:
        state (State): 현재 그래프의 상태 (메시지 리스트 및 그래프 데이터 포함)
    
    Returns:
        dict: 업데이트할 상태 {"messages": [AI 응답 메시지]}
    
    동작 과정:
    1. state에서 graph_data 가져오기
    2. 그래프 데이터를 JSON 형태로 컨텍스트에 포함
    3. build_chat_model()로 LLM 인스턴스 생성
    4. 사용자 메시지 + 그래프 컨텍스트를 LLM에 전달하여 응답 생성
    5. 생성된 응답을 messages 리스트에 추가
    6. LLM이 선택한 엣지를 원본 데이터 구조 형태로 출력

    
    """
    # print("💬 select_edge 노드 실행 중...")
    
    # 1. 그래프 데이터 가져오기
    graph_data = state.get("graph_data", {})
    
    # 2. 그래프 데이터를 JSON 형태로 컨텍스트 변환
    context_message = ""
    if graph_data and "error" not in graph_data:
        summary = graph_data.get("summary", {})
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])
        
        # JSON 형태로 edges 데이터 구조 포함
        edges_json = json.dumps(edges, ensure_ascii=False, indent=2)
        
        # 그래프 정보를 텍스트로 구성
        context_message = f"""
        [그래프 데이터 컨텍스트]
        - 총 노드 수: {summary.get('total_nodes', 0)}개
        - 총 엣지 수: {summary.get('total_edges', 0)}개
        - 노드 타입: {', '.join(summary.get('node_types', []))}
        - 설명: {summary.get('description', '')}

        [엣지 데이터 구조 (JSON 형식)]
        {edges_json}

        위 그래프 데이터를 참고하여 사용자의 질문에 맞는 엣지를 찾아주세요.
        응답 형식: 아래의 output format에 맞춰 선택한 엣지 정보를 JSON으로 출력해줘, 이외에 절대 다른 내용은 출력하지 말아줘.
        참고 정보도 보여주지말고 딱 JSON만 보여줘. 데이터 재확인 과정이나 추가적인 설명은 절대 보여주지말고 최종 json 결과만 보여줘.

        output format:
        ```json
        {{
            "highlight": {{
                "id": "엣지ID",
                "source": "출발노드ID",
                "target": "도착노드ID",
                "label": "엣지라벨"
            }},
            "reason": "엣지를 선택한 이유 설명"
        }}
        ```
"""
        
        # print(f"📊 그래프 컨텍스트 포함: {summary.get('total_nodes', 0)}개 노드, {summary.get('total_edges', 0)}개 엣지")
    else:
        context_message = "[그래프 데이터를 로드하지 못했습니다. 일반적인 질문에 대해서만 답변할 수 있습니다.]"
        # print("⚠️  그래프 데이터 없이 실행")
    
    # 3. LLM 인스턴스 생성
    llm = build_chat_model(temperature=0.7)
    
    # 4. 기존 메시지에 컨텍스트 추가
    messages = state["messages"].copy()
    
    # 시스템 메시지로 컨텍스트 추가 (첫 번째 위치에)
    from langchain_core.messages import SystemMessage
    messages.insert(0, SystemMessage(content=context_message))
    
    # 5. LLM 호출 및 응답 반환
    response = llm.invoke(messages)
    return {"messages": [response]}


def get_node_edge_data(state: State):
    """
    ReactFlow 그래프 데이터를 JSON 파일에서 로드하는 노드
    
    Args:
        state (State): 현재 그래프의 상태
    
    Returns:
        dict: 업데이트할 상태 {"graph_data": {노드와 엣지 정보}}
    
    동작 과정:
    1. data/reactflow_graph_route_stop.json 파일 경로 설정
    2. JSON 파일을 읽어서 파싱
    3. LLM이 이해하기 쉬운 형태로 데이터 구조화
    4. state에 graph_data로 저장
    
    데이터 구조:
    - nodes: 노드 리스트 (id, type, label 등)
    - edges: 엣지 리스트 (source, target, label 등)
    - summary: 그래프 요약 정보 (노드 수, 엣지 수 등)
    """
    try:
        # 1. JSON 파일 경로 설정 (현재 파일 기준 상대 경로)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "data", "reactflow_graph_route_stop.json")
        
        # 2. JSON 파일 읽기
        with open(json_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # 3. LLM이 이해하기 쉬운 형태로 데이터 구조화
        # 노드 정보 추출 및 정리
        nodes = []
        for node in raw_data.get("nodes", []):
            node_info = {
                "id": node.get("id"),
                "type": node.get("type"),
                "label": node.get("data", {}).get("label", "")
            }
            # 추가 데이터가 있으면 포함
            if "position" in node:
                node_info["position"] = node["position"]
            if "parentId" in node:
                node_info["parentId"] = node["parentId"]
            nodes.append(node_info)
        
        # 엣지 정보 추출 및 정리
        edges = []
        for edge in raw_data.get("edges", []):
            edge_info = {
                "id": edge.get("id"),
                "source": edge.get("source"),
                "target": edge.get("target"),
                "label": edge.get("label", "")
            }
            edges.append(edge_info)
        
        # 4. 그래프 요약 정보 생성
        summary = {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "node_types": list(set(node.get("type") for node in nodes if node.get("type"))),
            "description": "버스 노선과 정류장 정보를 담은 ReactFlow 그래프 데이터"
        }
        
        # 5. 구조화된 데이터 생성
        structured_data = {
            "summary": summary,
            "nodes": nodes,
            "edges": edges,
            "raw_data": raw_data  # 필요시 원본 데이터도 포함
        }
        
        # print(f"✅ 그래프 데이터 로드 완료: {summary['total_nodes']}개 노드, {summary['total_edges']}개 엣지")
        
        # 6. state 업데이트
        return {"graph_data": structured_data}
        
    except FileNotFoundError:
        error_msg = f"❌ 파일을 찾을 수 없습니다: {json_path}"
        print(error_msg)
        return {"graph_data": {"error": error_msg}}
    except json.JSONDecodeError as e:
        error_msg = f"❌ JSON 파싱 오류: {str(e)}"
        print(error_msg)
        return {"graph_data": {"error": error_msg}}
    except Exception as e:
        error_msg = f"❌ 데이터 로드 중 오류 발생: {str(e)}"
        print(error_msg)
        return {"graph_data": {"error": error_msg}}

def find_highlight_edge(state: State):
    """
    하이라이트할 엣지를 찾는 노드 (구현 예정)
    
    Args:
        state (State): 현재 그래프의 상태
    
    Returns:
        dict: 빈 딕셔너리 (상태 유지)
    """
    # print("🔍 find_highlight_edge 노드 실행 중...")
    # graph_data = state.get("graph_data", {})
    # 
    # if "error" in graph_data:
    #     print(f"⚠️  그래프 데이터 로드 실패: {graph_data.get('error')}")
    # else:
    #     summary = graph_data.get("summary", {})
    #     print(f"📊 로드된 그래프: {summary.get('total_nodes', 0)}개 노드, {summary.get('total_edges', 0)}개 엣지")
    
    # TODO: LLM을 사용하여 사용자 질문에 해당하는 엣지 찾기
    return {}  # 빈 딕셔너리 반환 (상태 변경 없음)

def highlighting_edge(state: State):
    """
    선택된 엣지를 하이라이트하는 노드 (구현 예정)
    
    Args:
        state (State): 현재 그래프의 상태
    
    Returns:
        dict: 빈 딕셔너리 (상태 유지)
    """
    # print("🎨 highlighting_edge 노드 실행 중...")
    
    # TODO: 하이라이트 로직 구현
    return {}  # 빈 딕셔너리 반환 (상태 변경 없음)

# ============================================================
# 4. 그래프 생성 함수
# ============================================================
def create_graph():
    """
    LangGraph 그래프를 생성하고 설정합니다.
    
    Returns:
        CompiledGraph: 실행 가능한 컴파일된 그래프
    
    그래프 구조:
        START → select_edge → END
    
    동작 흐름:
    1. StateGraph(State)로 그래프 빌더 생성
    2. "select_edge" 노드 추가 (위에서 정의한 select_edge 함수 사용)
    3. START에서 select_edge으로 가는 엣지(화살표) 추가
    4. select_edge에서 END로 가는 엣지 추가
    5. compile()로 그래프를 실행 가능한 형태로 컴파일
    """
    graph_builder = StateGraph(State)  # State 타입을 사용하는 그래프 빌더 생성
    
    # 노드 추가: "select_edge"이라는 이름으로 select_edge 함수를 노드로 등록
    graph_builder.add_node("get_node_edge_data", get_node_edge_data)
    graph_builder.add_node("select_edge", select_edge)
    graph_builder.add_node("find_highlight_edge", find_highlight_edge)
    graph_builder.add_node("highlighting_edge", highlighting_edge)
    # 엣지 추가: START(시작점) → select_edge 노드로 연결
    graph_builder.add_edge(START, "get_node_edge_data")
    graph_builder.add_edge("get_node_edge_data", "select_edge")
    graph_builder.add_edge("select_edge", "find_highlight_edge")
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
            # print("\n🤔 생각 중...\n")
            
            response = graph.invoke({
                "messages": [("user", user_input)]
            })
            # 실행 흐름:
            # a) START → select_edge 노드로 이동
            # b) select_edge 함수 실행: LLM이 응답 생성
            # c) select_edge → get_node_edge_data 노드로 이동
            # d) find_highlight_edge → highlighting_edge → END
            # e) 최종 상태(response) 반환
            
            # 5. AI 응답 출력 (JSON만 출력)
            # response['messages'][-1]: 메시지 리스트의 마지막 요소 (AI 응답)
            # .content: 메시지 객체의 실제 텍스트 내용
            print(f"{response['messages'][-1].content}")
            # print("-" * 60)
            
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
