'use client';

import { useRef, useEffect } from 'react';

interface VideoPlayerProps {
  videoUrl: string;
  onVideoEnded: () => void;
}

export function VideoPlayer({ videoUrl, onVideoEnded }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    // Reset video when url changes
    if (videoRef.current) {
      videoRef.current.load();
      videoRef.current.play().catch(err => {
        console.error("Error playing video:", err);
      });
    }
  }, [videoUrl]);

  return (
    <div className="relative mb-4 bg-black rounded-lg overflow-hidden shadow-lg">
      <video 
        ref={videoRef}
        className="w-full max-h-[500px] object-cover"
        onEnded={onVideoEnded}
        controls
        autoPlay
        muted
      >
        <source src={videoUrl} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
    </div>
  );
} 