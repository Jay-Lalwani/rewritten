'use client';

import { useState } from 'react';
// Import FontAwesomeIcon and specific icons
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPencilAlt } from '@fortawesome/free-solid-svg-icons';

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
    <div id="decision-container" className="mb-4">
      <h4 className="decisions-heading">
        {/* Replace me-2 with Tailwind mr-2 */}
        <FontAwesomeIcon icon={faPencilAlt} className="mr-2" /> Your Decision
      </h4>
      
      {/* Replace Bootstrap row/cols with Tailwind grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4" id="decision-options">
        {options.map(option => (
          // Grid item - col-span is implied by grid-cols-X on parent
          <div key={option.id} className="">
            <div
              className={`decision-card ${selectedOption === option.id ? 'selected' : ''}`}
              style={{ cursor: enabled ? 'pointer' : 'default', opacity: enabled ? 1 : 0.7 }}
              onClick={() => handleOptionClick(option.id)}
            >
              <p className="card-text">{option.option}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 