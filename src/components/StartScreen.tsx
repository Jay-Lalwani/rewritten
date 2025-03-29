'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

interface ScenarioProps {
  name: string;
  onSelect: (scenario: string) => void;
  onDelete: (scenario: string) => void;
}

function ScenarioCard({ name, onSelect, onDelete }: ScenarioProps) {
  return (
    <div className="col-span-1 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
      <div 
        className="p-4 cursor-pointer" 
        onClick={() => onSelect(name)}
      >
        <div className="text-center text-2xl mb-2">
          <i className="fas fa-landmark"></i>
        </div>
        <h5 className="text-lg font-medium text-center">{name}</h5>
        <button 
          className="mt-2 p-1 bg-red-600 text-white rounded-sm"
          onClick={(e) => {
            e.stopPropagation();
            onDelete(name);
          }}
        >
          <i className="fas fa-trash-alt"></i>
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
    <div className="text-center py-5">
      <div>
        <h2 className="text-2xl font-bold mb-6">Choose a Historical Moment to Begin</h2>
        
        {isLoading ? (
          <div className="text-center">Loading scenarios...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-4xl mx-auto">
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
        
        <div className="mt-8">
          <button 
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            onClick={() => setShowModal(true)}
          >
            <i className="fas fa-plus mr-2"></i>
            Create New Scenario
          </button>
        </div>
      </div>

      {/* Modal Dialog */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg w-full max-w-md">
            <h3 className="text-xl font-bold mb-4">Create a New Scenario</h3>
            <form onSubmit={handleAddScenario}>
              <div className="mb-4">
                <label className="block text-gray-700 mb-2">Historical Scenario Name</label>
                <input
                  type="text"
                  className="w-full p-2 border border-gray-300 rounded"
                  value={newScenarioName}
                  onChange={(e) => setNewScenarioName(e.target.value)}
                  placeholder="Enter historical scenario name..."
                  required
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  className="px-4 py-2 border border-gray-300 rounded"
                  onClick={() => setShowModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded"
                >
                  Add Scenario
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
} 