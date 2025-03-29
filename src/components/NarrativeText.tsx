'use client';

// Import FontAwesomeIcon and specific icons
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBookOpen } from '@fortawesome/free-solid-svg-icons';

interface NarrativeTextProps {
  narrative: string;
}

export function NarrativeText({ narrative }: NarrativeTextProps) {
  return (
    <div id="narrative-container" className="h-full">
      <h4 className="narrative-heading">
        <FontAwesomeIcon icon={faBookOpen} className="mr-2"/> The Story
      </h4>
      <div id="narrative-text" className="mt-3 p-3">
        {narrative}
      </div>
    </div>
  );
} 