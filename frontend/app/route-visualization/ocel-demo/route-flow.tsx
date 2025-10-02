'use client';

import { RouteStartNode } from './route-start-node';
import { RouteEndNode } from './route-end-node';
import { RouteStopNode } from './route-stop-node';
import { RouteEdgeComponent } from './route-edge';
import { type Edge, type Node, ReactFlow, useEdgesState, useNodesState, Controls, MiniMap, Background, BackgroundVariant } from 'reactflow';
import 'reactflow/dist/style.css';
import * as dagre from 'dagre';
import type React from 'react';
import { useCallback, useEffect } from 'react';
import { RouteGraphData, RouteNode, EnrichedEdge } from '../types/route.types';

const nodeTypes = {
  routeStop: RouteStopNode,
  routeStart: RouteStartNode,
  routeEnd: RouteEndNode,
};

const edgeTypes = {
  routeEdge: RouteEdgeComponent,
};

interface RouteFlowProps {
  routeData: RouteGraphData;
  enrichedEdges: EnrichedEdge[];
}

export const RouteFlow: React.FC<RouteFlowProps> = ({ routeData, enrichedEdges }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  const applyDagreLayout = useCallback((flowNodes: Node[], flowEdges: Edge[]) => {
    if (!flowNodes.length) return { nodes: flowNodes, edges: flowEdges };

    try {
      const g = new dagre.graphlib.Graph();
      g.setGraph({
        rankdir: 'TB',
        ranker: 'network-simplex',
        nodesep: 160,
        ranksep: 120,
      });

      g.setDefaultEdgeLabel(() => ({}));

      flowNodes.forEach((node) => {
        g.setNode(node.id, {
          width: 240,
          height: node.type === 'routeStart' || node.type === 'routeEnd' ? 72 : 56,
        });
      });

      flowEdges.forEach((edge) => {
        g.setEdge(edge.source, edge.target);
      });

      dagre.layout(g);

      const layoutedNodes = flowNodes.map((node) => {
        const gNode = g.node(node.id);
        return {
          ...node,
          position: {
            x: gNode.x - gNode.width / 2,
            y: gNode.y - gNode.height / 2,
          },
        };
      });

      return { nodes: layoutedNodes, edges: flowEdges };
    } catch (error) {
      console.error('Error in dagre layout:', error);
      return { nodes: flowNodes, edges: flowEdges };
    }
  }, []);

  useEffect(() => {
    // 그룹 노드와 일반 노드 분리
    const stopNodes = routeData.nodes.filter((node: RouteNode) => node.type !== 'group');
    const groupNodes = routeData.nodes.filter((node: RouteNode) => node.type === 'group');

    // 노선명 매핑
    const routeNameMap = new Map<string, string>();
    groupNodes.forEach((node: RouteNode) => {
      routeNameMap.set(node.id, (node.data as any).label);
    });

    // 시작 노드 생성
    const startNodes: Node[] = Array.from(routeNameMap.entries()).map(([routeId, routeName]) => ({
      id: `start-${routeId}`,
      type: 'routeStart',
      data: {
        routeName,
      },
      position: { x: 0, y: 0 }, // dagre will calculate actual position
    }));

    // 종료 노드 생성
    const endNodes: Node[] = Array.from(routeNameMap.entries()).map(([routeId, routeName]) => ({
      id: `end-${routeId}`,
      type: 'routeEnd',
      data: {
        routeName,
      },
      position: { x: 0, y: 0 }, // dagre will calculate actual position
    }));

    // 정류장 노드 변환
    const stopNodesTransformed: Node[] = stopNodes.map((node: RouteNode) => ({
      id: node.id,
      type: 'routeStop',
      data: node.data,
      position: { x: 0, y: 0 }, // dagre will calculate actual position
    }));

    const initialNodes = [...startNodes, ...stopNodesTransformed, ...endNodes];

    // 시작 노드와 첫 번째 정류장 연결 엣지 생성
    const startEdges: Edge[] = Array.from(routeNameMap.keys())
      .map((routeId) => {
        const firstStop = stopNodes.find((node) => node.parentNode === routeId);
        if (!firstStop) return null;

        return {
          id: `edge-start-${routeId}`,
          source: `start-${routeId}`,
          target: firstStop.id,
          type: 'routeEdge',
          animated: false,
          data: {
            currentPassengers: 0,
            isStartEdge: true,
          },
        };
      })
      .filter(Boolean) as Edge[];

    // 정류장 간 연결 엣지
    const stopEdges: Edge[] = enrichedEdges.map((edge: EnrichedEdge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: 'routeEdge',
      animated: true,
      data: {
        currentPassengers: edge.currentPassengers,
        isStartEdge: false,
      },
    }));

    // 마지막 정류장과 종료 노드 연결 엣지 생성
    const endEdges: Edge[] = Array.from(routeNameMap.keys())
      .map((routeId) => {
        // 해당 노선의 마지막 정류장 찾기
        const routeStops = stopNodes.filter((node) => node.parentNode === routeId);
        if (routeStops.length === 0) return null;

        // ID의 숫자 부분으로 정렬하여 마지막 정류장 찾기
        const sortedStops = routeStops.sort((a, b) => {
          const aNum = parseInt(a.id.split('::')[1] || '0');
          const bNum = parseInt(b.id.split('::')[1] || '0');
          return aNum - bNum;
        });
        const lastStop = sortedStops[sortedStops.length - 1];

        return {
          id: `edge-end-${routeId}`,
          source: lastStop.id,
          target: `end-${routeId}`,
          type: 'routeEdge',
          animated: false,
          data: {
            currentPassengers: 0,
            isStartEdge: true,
          },
        };
      })
      .filter(Boolean) as Edge[];

    const initialEdges = [...startEdges, ...stopEdges, ...endEdges];

    // Apply dagre layout
    const { nodes: layoutedNodes, edges: layoutedEdges } = applyDagreLayout(initialNodes, initialEdges);

    setNodes(layoutedNodes);
    setEdges(layoutedEdges);
  }, [routeData, enrichedEdges, applyDagreLayout, setNodes, setEdges]);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      nodeTypes={nodeTypes}
      edgeTypes={edgeTypes}
      fitView
      attributionPosition="bottom-right"
      style={{ background: '#0f172a', width: '100%', height: '100%' }}
    >
      <Controls style={{ position: 'absolute', top: 10, left: 10 }} />
      <MiniMap
        zoomable
        pannable
        nodeColor="#1e293b"
        style={{
          background: '#1e293b',
          position: 'absolute',
          bottom: 10,
          right: 10
        }}
      />
      <Background variant={BackgroundVariant.Dots} gap={12} size={1} color="#334155" />
    </ReactFlow>
  );
};
