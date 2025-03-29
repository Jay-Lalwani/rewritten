'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faLandmark, faTrashAlt, faPlus } from '@fortawesome/free-solid-svg-icons';

interface ScenarioProps {
  name: string;
  onSelect: (scenario: string) => void;
  onDelete: (scenario: string) => void;
}

function ScenarioCard({ name, onSelect, onDelete }: ScenarioProps) {
  return (
    <div className="col-span-1 scenario-card">
      <div 
        className="card-body"
        onClick={() => onSelect(name)}
      >
        <div className="scenario-icon">
          <FontAwesomeIcon icon={faLandmark} />
        </div>
        <h5 className="card-title">{name}</h5>
        <button 
          className="delete-scenario text-red-600 hover:text-red-800 text-sm p-1"
          onClick={(e) => {
            e.stopPropagation();
            onDelete(name);
          }}
        >
          <FontAwesomeIcon icon={faTrashAlt} />
        </button>
      </div>
    </div>
  );
}

interface StartScreenProps {
  onStart: (scenario: string) => void;
}

export function StartScreen({ onStart }: StartScreenProps) {
  const [scenarios, setScenarios] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [newScenarioName, setNewScenarioName] = useState('');
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    async function loadScenarios() {
      setIsLoading(true);
      const response = await api.scenarios.getAll();
      if (response.data) {
        setScenarios(response.data.scenarios || []);
      }
      setIsLoading(false);
    }
    
    loadScenarios();
  }, []);

  const handleAddScenario = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newScenarioName.trim()) {
      const response = await api.scenarios.create(newScenarioName.trim());
      if (response.data?.success) {
        setScenarios([...scenarios, response.data.scenario]);
        setNewScenarioName('');
        setShowModal(false);
      }
    }
  };

  const handleDeleteScenario = async (scenarioName: string) => {
    const response = await api.scenarios.delete(scenarioName);
    if (response.data?.success) {
      setScenarios(scenarios.filter(s => s !== scenarioName));
    }
  };

  return (
    <div id="start-screen" className="text-center">
      <div className="start-content">
        <h2 className="text-center">Choose a Historical Moment to Begin</h2>
        
        {isLoading ? (
          <div className="text-center mt-5">Loading scenarios...</div>
        ) : (
          <div id="scenario-container" className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12 max-w-4xl mx-auto">
            {scenarios.map(scenario => (
              <ScenarioCard 
                key={scenario}
                name={scenario}
                onSelect={onStart}
                onDelete={handleDeleteScenario}
              />
            ))}
          </div>
        )}
        
        <div className="text-center mt-8">
          <button 
            type="button"
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
            onClick={() => setShowModal(true)}
          >
            <FontAwesomeIcon icon={faPlus} className="mr-2" />
            Create New Scenario
          </button>
        </div>
      </div>

      {showModal && (
        <div 
          id="addScenarioModal" 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
        >
          <div className="bg-white p-6 rounded-lg shadow-xl w-full max-w-md mx-4">
            <div className="flex justify-between items-center border-b pb-3 mb-4">
              <h5 className="text-xl font-semibold">Create a New Scenario</h5>
              <button 
                type="button" 
                className="text-gray-500 hover:text-gray-700 text-2xl" 
                onClick={() => setShowModal(false)}
                aria-label="Close"
              >
                &times;
              </button>
            </div>
            <div>
              <form id="new-scenario-form" onSubmit={handleAddScenario}>
                <div className="mb-4">
                  <label htmlFor="new-scenario-name" className="block text-sm font-medium text-gray-700 mb-1">Historical Scenario Name</label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                    id="new-scenario-name"
                    value={newScenarioName}
                    onChange={(e) => setNewScenarioName(e.target.value)}
                    placeholder="Enter historical scenario name..."
                    required
                  />
                </div>
                <div className="flex justify-end mt-6">
                  <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors flex items-center">
                    <FontAwesomeIcon icon={faPlus} className="mr-2" />Add Scenario
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 