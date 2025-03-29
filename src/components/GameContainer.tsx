'use client';

import { useState, useEffect } from 'react';
import { VideoPlayer } from './VideoPlayer';
import { NarrativeText } from './NarrativeText';
import { DecisionOptions } from './DecisionOptions';
import { api } from '@/lib/api';

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
    return (
      <div className="flex flex-col items-center justify-center py-10">
        <h3 className="text-2xl mb-4">Rewriting History...</h3>
        <div className="animate-spin text-3xl mb-4">
          <span>⏳</span>
        </div>
        <p>Generating your unique historical narrative.</p>
      </div>
    );
  }
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 py-4">
      <div className="md:col-span-2">
        {/* Left Column: Video and Decisions */}
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
        
        {/* Progress Tracker */}
        {decisions.length > 0 && (
          <div className="bg-white p-4 rounded-lg shadow-md">
            <h5 className="text-lg font-serif border-b-2 border-amber-500 pb-2 mb-3">
              <i className="fas fa-history mr-2"></i> Your Journey
            </h5>
            <div className="flex flex-col space-y-2">
              {decisions.map((decision, index) => (
                <div 
                  key={index}
                  className="p-3 bg-gray-100 rounded-md flex items-center"
                >
                  <div className="mr-3 text-amber-600">
                    <i className="fas fa-chevron-right"></i>
                  </div>
                  <div>
                    <span className="font-medium">Scene {decision.scene_id}:</span> {decision.decision_text}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      
      <div className="md:col-span-1">
        {/* Right Column: Narrative */}
        {currentScene && (
          <NarrativeText narrative={currentScene.narrative} />
        )}
        
        <button 
          onClick={onExit}
          className="mt-4 px-4 py-2 bg-slate-700 text-white rounded-md hover:bg-slate-800"
        >
          <i className="fas fa-arrow-left mr-2"></i> Return to Scenarios
        </button>
      </div>
    </div>
  );
} 