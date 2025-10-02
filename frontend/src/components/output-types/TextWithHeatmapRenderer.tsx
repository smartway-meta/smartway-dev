'use client';

import { Message as MessageType } from '@/lib/types';
import { HeatmapRenderer } from '@/components/charts/HeatmapRenderer';

interface TextWithHeatmapRendererProps {
  message: MessageType;
  renderHint?: Record<string, any>;
}

// Helper function to convert chart data to heatmap format
function convertToHeatmapData(chartData: any[], heatmapConfig?: any) {
  if (!Array.isArray(chartData) || chartData.length === 0) return [];

  // Try to detect heatmap data structure
  const firstRow = chartData[0];
  const keys = Object.keys(firstRow);
  
  // Look for x, y, value pattern
  if (keys.includes('x') && keys.includes('y') && keys.includes('v')) {
    return chartData.map(item => ({
      x: item.x,
      y: item.y,
      v: Number(item.v) || 0,
    }));
  }

  // Try alternative patterns
  if (keys.includes('x') && keys.includes('y') && keys.includes('value')) {
    return chartData.map(item => ({
      x: item.x,
      y: item.y,
      v: Number(item.value) || 0,
    }));
  }

  // If heatmap config provides column mappings, use them
  if (heatmapConfig?.x_column && heatmapConfig?.y_column && heatmapConfig?.value_column) {
    return chartData.map(item => ({
      x: item[heatmapConfig.x_column],
      y: item[heatmapConfig.y_column], 
      v: Number(item[heatmapConfig.value_column]) || 0,
    }));
  }

  // Default fallback - try to create grid from first 3 columns
  if (keys.length >= 3) {
    return chartData.map(item => ({
      x: item[keys[0]],
      y: item[keys[1]],
      v: Number(item[keys[2]]) || 0,
    }));
  }

  return [];
}

export function TextWithHeatmapRenderer({ 
  message, 
  renderHint 
}: TextWithHeatmapRendererProps) {
  // output_type: text+heatmap always renders data as a heatmap visualization
  // Convert chart data to heatmap format
  const heatmapData = message.chart_data ? 
    convertToHeatmapData(message.chart_data, renderHint?.heatmap_config) : [];

  // Prepare heatmap configuration
  const heatmapConfig = {
    title: renderHint?.title || 'Heatmap Analysis',
    description: renderHint?.description,
    x_axis_label: renderHint?.heatmap_config?.x_axis || renderHint?.x_axis || 'X-axis',
    y_axis_label: renderHint?.heatmap_config?.y_axis || renderHint?.y_axis || 'Y-axis',
    color_scheme: renderHint?.heatmap_config?.color_scheme || 'blues',
    min_value: renderHint?.heatmap_config?.min_value,
    max_value: renderHint?.heatmap_config?.max_value,
    ...renderHint?.heatmap_config,
  };

  // Calculate heatmap statistics
  const getHeatmapStats = () => {
    if (!heatmapData || heatmapData.length === 0) return null;

    const values = heatmapData.map(d => d.v);
    const xValues = Array.from(new Set(heatmapData.map(d => String(d.x))));
    const yValues = Array.from(new Set(heatmapData.map(d => String(d.y))));

    return {
      totalCells: heatmapData.length,
      xDimensions: xValues.length,
      yDimensions: yValues.length,
      minValue: Math.min(...values),
      maxValue: Math.max(...values),
      avgValue: values.reduce((a, b) => a + b, 0) / values.length,
    };
  };

  const heatmapStats = getHeatmapStats();

  return (
    <div className="text-with-heatmap space-y-6">
            
      {/* Heatmap and analysis layout - only show if data exists */}
      {heatmapData.length > 0 && (
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
          {/* Heatmap - spans 3 columns on extra large screens */}
          <div className="xl:col-span-3">
            <HeatmapRenderer 
              data={heatmapData}
              config={heatmapConfig}
              height={250}
              className="w-full"
            />
          </div>
        
        {/* Analysis and correlation panel */}
        <div className="xl:col-span-1 space-y-4">
          {/* Heatmap statistics */}
          {heatmapStats && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <h4 className="font-semibold text-red-900 mb-3 flex items-center">
                <span className="mr-2">📊</span>
                Heatmap Statistics
              </h4>
              <div className="space-y-2 text-sm text-red-800">
                <div className="flex justify-between">
                  <span>Total Cells:</span>
                  <span className="font-medium">{heatmapStats.totalCells}</span>
                </div>
                <div className="flex justify-between">
                  <span>X-axis Range:</span>
                  <span className="font-medium">{heatmapStats.xDimensions}</span>
                </div>
                <div className="flex justify-between">
                  <span>Y-axis Range:</span>
                  <span className="font-medium">{heatmapStats.yDimensions}</span>
                </div>
                <div className="pt-2 border-t border-red-300">
                  <div className="flex justify-between">
                    <span>Min Value:</span>
                    <span className="font-medium">{heatmapStats.minValue.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Max Value:</span>
                    <span className="font-medium">{heatmapStats.maxValue.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Average:</span>
                    <span className="font-medium">{heatmapStats.avgValue.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Correlation insights */}
          {renderHint?.insights && Array.isArray(renderHint.insights) && (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="font-semibold text-blue-900 mb-3 flex items-center">
                <span className="mr-2">🔗</span>
                상관관계 분석
              </h4>
              <ul className="space-y-2 text-sm text-blue-800">
                {renderHint.insights.map((insight: string, idx: number) => (
                  <li key={idx} className="flex items-start">
                    <span className="text-blue-600 mr-2 mt-0.5">•</span>
                    <span className="leading-relaxed">{insight}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Pattern analysis */}
          {renderHint?.patterns && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <h4 className="font-semibold text-green-900 mb-2 flex items-center">
                <span className="mr-2">🎨</span>
                패턴 분석
              </h4>
              <p className="text-sm text-green-800 leading-relaxed">
                {renderHint.patterns}
              </p>
            </div>
          )}

          {/* Hot spots identification */}
          {renderHint?.hot_spots && Array.isArray(renderHint.hot_spots) && (
            <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
              <h4 className="font-semibold text-orange-900 mb-3 flex items-center">
                <span className="mr-2">🔥</span>
                핫스팟 영역
              </h4>
              <ul className="space-y-2 text-sm text-orange-800">
                {renderHint.hot_spots.map((spot: string, idx: number) => (
                  <li key={idx} className="flex items-start">
                    <span className="text-orange-600 mr-2 mt-0.5">▲</span>
                    <span className="leading-relaxed">{spot}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Interpretation guide */}
          <div className="p-4 bg-gray-100 border border-gray-300 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
              <span className="mr-2">📖</span>
              해석 가이드
            </h4>
            <ul className="space-y-1 text-xs text-gray-600">
              <li>• 진한 색상: 높은 값/강한 상관관계</li>
              <li>• 연한 색상: 낮은 값/약한 상관관계</li>
              <li>• 클러스터링: 유사한 패턴 그룹</li>
              <li>• 대각선 패턴: 순차적 상관관계</li>
            </ul>
          </div>

          {/* Color scheme info */}
          <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <h4 className="font-semibold text-purple-900 mb-2 flex items-center">
              <span className="mr-2">🎨</span>
              색상 스킴
            </h4>
            <p className="text-sm text-purple-800">
              현재 사용: <span className="font-medium">{heatmapConfig.color_scheme}</span>
            </p>
            <div className="mt-2 text-xs text-purple-700">
              값의 강도에 따라 색상 농도가 변화합니다
            </div>
          </div>
        </div>
        </div>
      )}

      {/* Additional interpretation or context */}
      {renderHint?.interpretation && (
        <div className="mt-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
            <span className="mr-2">🔍</span>
            상세 해석
          </h4>
          <p className="text-gray-700 leading-relaxed">
            {renderHint.interpretation}
          </p>
        </div>
      )}

      {/* Metadata */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="text-xs text-gray-500 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <span>시각화 유형: 히트맵 (2차원 상관관계)</span>
            {heatmapStats && (
              <span>{heatmapStats.xDimensions}×{heatmapStats.yDimensions} 매트릭스</span>
            )}
          </div>
          {renderHint?.confidence && (
            <span>분석 신뢰도: {Math.round(renderHint.confidence * 100)}%</span>
          )}
        </div>
      </div>
    </div>
  );
}