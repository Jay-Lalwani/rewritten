'use client';

import { useState } from 'react';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { StartScreen } from '@/components/StartScreen';
import { GameContainer } from '@/components/GameContainer';

export default function Home() {
  const [gameState, setGameState] = useState<'start' | 'loading' | 'playing'>('start');
  const [currentScenario, setCurrentScenario] = useState<string | null>(null);
  
  const handleStartGame = (scenario: string) => {
    setCurrentScenario(scenario);
    setGameState('loading');
    
    // Simulate brief loading time before showing game
    setTimeout(() => {
      setGameState('playing');
    }, 1000);
  };
  
  const handleExitGame = () => {
    setGameState('start');
    setCurrentScenario(null);
  };
  
  return (
    <main className="min-h-screen flex flex-col">
      <Header />
      
      <div className="flex-grow container mx-auto px-4 pb-16">
        {gameState === 'start' && (
          <StartScreen onStart={handleStartGame} />
        )}
        
        {gameState === 'loading' && (
          <div className="flex flex-col items-center justify-center h-full py-10">
            <h3 className="text-2xl mb-4">Rewriting History...</h3>
            <div className="animate-spin text-3xl mb-4">
              <span>⏳</span>
            </div>
            <p>Generating your unique historical narrative.</p>
          </div>
        )}
        
        {gameState === 'playing' && currentScenario && (
          <GameContainer 
            scenario={currentScenario} 
            onExit={handleExitGame}
          />
        )}
      </div>
      
      <Footer />
    </main>
  );
} 