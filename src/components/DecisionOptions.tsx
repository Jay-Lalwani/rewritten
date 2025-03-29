'use client';

import { useState } from 'react';

interface Option {
  id: string;
  option: string;
}

interface DecisionOptionsProps {
  options: Option[];
  onDecisionMade: (decisionId: string) => void;
  enabled: boolean;
}

export function DecisionOptions({ options, onDecisionMade, enabled }: DecisionOptionsProps) {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);

  const handleOptionClick = (optionId: string) => {
    if (!enabled) return;
    
    setSelectedOption(optionId);
    onDecisionMade(optionId);
  };

  return (
    <div className="mb-8">
      <h4 className="text-xl font-serif border-b-2 border-amber-500 pb-2 mb-4">
        <i className="fas fa-pencil-alt mr-2"></i> Your Decision
      </h4>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {options.map(option => (
          <div
            key={option.id}
            className={`
              p-4 border-2 rounded-lg cursor-pointer transition-all
              ${enabled ? 'hover:shadow-lg hover:-translate-y-1' : 'opacity-70'}
              ${selectedOption === option.id 
                ? 'bg-red-600 text-white border-slate-800' 
                : 'bg-white border-slate-800'}
            `}
            onClick={() => handleOptionClick(option.id)}
          >
            <p className="text-lg">{option.option}</p>
          </div>
        ))}
      </div>
    </div>
  );
} 