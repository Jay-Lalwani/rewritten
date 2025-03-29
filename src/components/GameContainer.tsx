'use client';

import { useState, useEffect } from 'react';
import { VideoPlayer } from './VideoPlayer';
import { NarrativeText } from './NarrativeText';
import { DecisionOptions } from './DecisionOptions';
import { api } from '@/lib/api';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFeatherAlt, faHistory, faArrowLeft } from '@fortawesome/free-solid-svg-icons';

interface GameContainerProps {
  scenario: string;
  onExit: () => void;
}

interface Decision {
  scene_id: number;
  decision: string;
  decision_text: string;
}

interface Option {
  id: string;
  option: string;
}

interface NarrativeScene {
  scene_id: number;
  narrative: string;
  options: Option[];
}

export function GameContainer({ scenario, onExit }: GameContainerProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [currentScene, setCurrentScene] = useState<NarrativeScene | null>(null);
  const [videoUrl, setVideoUrl] = useState('');
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [videoEnded, setVideoEnded] = useState(false);
  
  useEffect(() => {
    // Start the game when component mounts
    startGame();
  }, []);
  
  const startGame = async () => {
    setIsLoading(true);
    
    // Call the Flask API to start a game session
    const response = await api.game.start(scenario);
    
    if (response.data) {
      setCurrentScene(response.data.narrative);
      setVideoUrl(response.data.media);
      setDecisions([]);
      setVideoEnded(false);
    } else {
      // Handle errors
      console.error('Failed to start game:', response.error);
    }
    
    setIsLoading(false);
  };
  
  const handleVideoEnded = () => {
    setVideoEnded(true);
  };
  
  const handleDecisionMade = async (decisionId: string) => {
    if (!currentScene) return;
    
    setIsLoading(true);
    setVideoEnded(false);
    
    // Add decision to history
    const selectedOption = currentScene.options.find(opt => opt.id === decisionId);
    const newDecision = {
      scene_id: currentScene.scene_id,
      decision: decisionId,
      decision_text: selectedOption?.option || ''
    };
    
    // Call the Flask API to process the decision
    const response = await api.game.makeDecision(currentScene.scene_id, decisionId);
    
    if (response.data) {
      setCurrentScene(response.data.narrative);
      setVideoUrl(response.data.media);
      setDecisions([...decisions, newDecision]);
    } else {
      // Handle errors
      console.error('Failed to process decision:', response.error);
    }
    
    setIsLoading(false);
  };
  
  if (isLoading) {
    // Use the #loading-screen ID and structure from original HTML
    return (
      <div id="loading-screen" className="text-center p-5">
        <div className="loading-content">
          <div className="typewriter">
            <h3>Rewriting History...</h3>
          </div>
          <div className="spinner">
            <FontAwesomeIcon icon={faFeatherAlt} spin size="3x" />
          </div>
          <p className="mt-4">Generating your unique historical narrative.</p>
        </div>
      </div>
    );
  }
  
  return (
    // Apply #game-container ID
    <div id="game-container">
      {/* Replace Bootstrap row with Tailwind grid - adjust gap as needed */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column - Use Tailwind grid column span */}
        <div className="md:col-span-2 game-left-column">
          <VideoPlayer 
            videoUrl={videoUrl} 
            onVideoEnded={handleVideoEnded} 
          />
          
          {currentScene && (
            <DecisionOptions 
              options={currentScene.options}
              onDecisionMade={handleDecisionMade}
              enabled={videoEnded}
            />
          )}
          
          {decisions.length > 0 && (
            <div id="progress-tracker" className="p-3 mb-4">
              {/* Replace me-2 with Tailwind mr-2 */}
              <h5><FontAwesomeIcon icon={faHistory} className="mr-2" /> Your Journey</h5>
              {/* Replace Bootstrap flex with Tailwind flex */}
              <div id="progress-path" className="flex flex-col space-y-2">
                {decisions.map((decision, index) => (
                  <div key={index} className="progress-item">
                    <div>
                       <span className="font-medium">Scene {decision.scene_id}:</span> {decision.decision_text}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        
        {/* Right Column - Use Tailwind grid column span */}
        <div className="md:col-span-1 game-right-column">
          {currentScene && (
            <NarrativeText narrative={currentScene.narrative} />
          )}
          
          {/* Exit button - already uses Tailwind */}
          <button 
            onClick={onExit}
            className="mt-4 px-4 py-2 bg-slate-700 text-white rounded-md hover:bg-slate-800" 
          >
            {/* Replace me-2 with Tailwind mr-2 */}
            <FontAwesomeIcon icon={faArrowLeft} className="mr-2" /> Return to Scenarios
          </button>
        </div>
      </div>
    </div>
  );
} 