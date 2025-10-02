'use client';

import React from 'react';
import { Message as MessageType, StrategicSuggestionsData, StrategicImprovement } from '@/lib/types';

interface StrategicSuggestionsRendererProps {
  message: MessageType;
  renderHint?: Record<string, any>;
}

export function StrategicSuggestionsRenderer({ 
  message, 
  renderHint 
}: StrategicSuggestionsRendererProps) {
  // Extract strategic suggestions data from message
  const strategicData: StrategicSuggestionsData = message.chart_data as any || renderHint?.strategic_data || {
    title: "AI-Generated Strategic Improvements",
    improvements: []
  };

  // Default improvements if no data is provided
  const defaultImprovements: StrategicImprovement[] = [
    {
      type: 'immediate_containment',
      title: 'Immediate Containment',
      description: 'Quarantine all remaining C-789 capacitors.',
      netsuiteAction: {
        label: 'NetSuite Action:',
        action: "Create Inventory Status Change to 'Quarantine'."
      }
    },
    {
      type: 'process_improvement',
      title: 'Process Improvement',
      description: 'Implement mandatory Incoming Quality Control (IQC) for all critical components.',
      netsuiteAction: {
        label: 'NetSuite Action:',
        action: "Update Item Receipt workflow to include a 'Pending Inspection' status."
      }
    },
    {
      type: 'supplier_action',
      title: 'Supplier Action',
      description: 'Initiate a Vendor Return Authorization for the faulty batch and flag Vendor-X for performance review.'
    }
  ];

  const improvements = strategicData.improvements.length > 0 ? strategicData.improvements : defaultImprovements;

  const getTypeColor = (type: StrategicImprovement['type']) => {
    switch (type) {
      case 'immediate_containment':
        return 'text-blue-300';
      case 'process_improvement':
        return 'text-blue-300';
      case 'supplier_action':
        return 'text-blue-300';
      default:
        return 'text-blue-300';
    }
  };

  return (
    <div className="strategic-suggestions-container">
      {/* Header */}
      <div className="bg-slate-800 border-b border-slate-700 px-4 py-4">
        <div className="flex items-center gap-2 bg-blue-500/10 px-2 py-1 rounded w-fit">
          <svg className="w-4 h-4 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M9.504 1.132a1 1 0 01.992 0l1.75 1a1 1 0 11-.992 1.736L10 3.152l-1.254.716a1 1 0 11-.992-1.736l1.75-1zM5.618 4.504a1 1 0 01-.372 1.364L5.016 6l.23.132a1 1 0 11-.992 1.736L3 7.723V8a1 1 0 01-2 0V6a.996.996 0 01.52-.878l1.734-.99a1 1 0 011.364.372zm8.764 0a1 1 0 011.364-.372l1.734.99A.996.996 0 0118 6v2a1 1 0 11-2 0v-.277l-1.254.145a1 1 0 11-.992-1.736L14.984 6l-.23-.132a1 1 0 01-.372-1.364zm-7 4a1 1 0 011.364-.372L10 8.848l1.254-.716a1 1 0 11.992 1.736L11 10.723V11a1 1 0 11-2 0v-.277l-1.246-.855a1 1 0 01-.372-1.364zM3 11a1 1 0 011 1v1.277l1.254.855a1 1 0 11-.992 1.736L3.5 15.5l-.738 1.276a1 1 0 01-1.732-1l.5-.866a1 1 0 01.866-.5H3a1 1 0 01-1-1zm14 0a1 1 0 011 1v1a1 1 0 01-1 1h-.866a1 1 0 01-.866.5l.5.866a1 1 0 11-1.732 1L16.5 15.5l-.762.368a1 1 0 11-.992-1.736L16 13.277V12a1 1 0 011-1zM9.504 16.132a1 1 0 01.992 0l1.75 1a1 1 0 11-.992 1.736L10 18.152l-1.254.716a1 1 0 11-.992-1.736l1.75-1z" clipRule="evenodd" />
          </svg>
          <span className="text-white text-sm font-normal">
            {strategicData.title}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="bg-slate-800 px-4 py-4">
        <div className="space-y-3">
          {improvements.map((improvement, index) => (
            <div key={index} className="space-y-0">
              {/* Main improvement section */}
              <div className="bg-blue-500/5 border-b border-slate-700 px-3 py-3">
                <div className="space-y-2">
                  <h3 className={`${getTypeColor(improvement.type)} text-base font-semibold leading-6 tracking-tight`}>
                    {improvement.title}
                  </h3>
                  <p className="text-white text-sm font-normal leading-5 tracking-tight">
                    {improvement.description}
                  </p>
                </div>
              </div>

              {/* NetSuite action section */}
              {improvement.netsuiteAction && (
                <div className="bg-blue-500/5 px-3 py-3">
                  <div className="space-y-1">
                    <p className="text-slate-400 text-sm font-normal leading-5 tracking-tight">
                      {improvement.netsuiteAction.label}
                    </p>
                    <p className="text-white text-sm font-normal leading-5 tracking-tight">
                      {improvement.netsuiteAction.action}
                    </p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}