from src.find_highlight_basic import create_graph

graph = create_graph()
print("그래프 생성 완료")
print("\n그래프 노드 목록:")
print(graph.get_graph().nodes)
print("\n그래프 엣지 목록:")
for edge in graph.get_graph().edges:
    print(f"  {edge}")
