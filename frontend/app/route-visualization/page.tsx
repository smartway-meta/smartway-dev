'use client';

import { useEffect, useState } from 'react';
import { RouteFlowWrapper } from './ocel-demo/route-flow-wrapper';
import { loadRouteData, calculateCurrentPassengers } from './utils/dataTransform';
import { RouteGraphData, EnrichedEdge } from './types/route.types';

export default function RouteVisualizationPage() {
  const [routeData, setRouteData] = useState<RouteGraphData | null>(null);
  const [enrichedEdges, setEnrichedEdges] = useState<EnrichedEdge[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await loadRouteData();
        const edges = calculateCurrentPassengers(data.nodes, data.edges);

        setRouteData(data);
        setEnrichedEdges(edges);
        setLoading(false);
      } catch (error) {
        console.error('Failed to load route data:', error);
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) {
    return (
      <div style={{ width: '100vw', height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#0f172a', color: 'white' }}>
        <div>Loading route data...</div>
      </div>
    );
  }

  if (!routeData) {
    return (
      <div style={{ width: '100vw', height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#0f172a', color: 'white' }}>
        <div>Failed to load route data</div>
      </div>
    );
  }

  return (
    <main style={{ width: '100vw', height: '100vh' }}>
      <RouteFlowWrapper routeData={routeData} enrichedEdges={enrichedEdges} />
    </main>
  );
}
