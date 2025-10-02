import React from 'react';
import { render, screen } from '@testing-library/react';
import { StrategicSuggestionsRenderer } from './StrategicSuggestionsRenderer';
import { Message } from '@/lib/types';

// Mock message with strategic suggestions data
const mockMessage: Message = {
  id: 'test-1',
  role: 'assistant',
  content: '',
  timestamp: new Date().toISOString(),
  output_type: 'strategic_suggestions',
  chart_data: {
    title: 'AI-Generated Strategic Improvements',
    improvements: [
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
    ]
  }
};

describe('StrategicSuggestionsRenderer', () => {
  it('renders strategic suggestions correctly', () => {
    render(<StrategicSuggestionsRenderer message={mockMessage} />);
    
    // Check if the title is rendered
    expect(screen.getByText('AI-Generated Strategic Improvements')).toBeInTheDocument();
    
    // Check if improvement titles are rendered
    expect(screen.getByText('Immediate Containment')).toBeInTheDocument();
    expect(screen.getByText('Process Improvement')).toBeInTheDocument();
    expect(screen.getByText('Supplier Action')).toBeInTheDocument();
    
    // Check if NetSuite actions are rendered
    expect(screen.getByText("Create Inventory Status Change to 'Quarantine'.")).toBeInTheDocument();
    expect(screen.getByText("Update Item Receipt workflow to include a 'Pending Inspection' status.")).toBeInTheDocument();
  });

  it('renders default improvements when no data is provided', () => {
    const emptyMessage: Message = {
      ...mockMessage,
      chart_data: undefined
    };
    
    render(<StrategicSuggestionsRenderer message={emptyMessage} />);
    
    // Should still render the default improvements
    expect(screen.getByText('AI-Generated Strategic Improvements')).toBeInTheDocument();
    expect(screen.getByText('Immediate Containment')).toBeInTheDocument();
  });
});