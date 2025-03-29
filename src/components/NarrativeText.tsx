'use client';

interface NarrativeTextProps {
  narrative: string;
}

export function NarrativeText({ narrative }: NarrativeTextProps) {
  return (
    <div className="h-full bg-amber-50 rounded-lg shadow-md overflow-y-auto">
      <h4 className="text-xl font-serif border-b-2 border-amber-500 p-4 text-slate-800">
        <i className="fas fa-book-open mr-2"></i> The Story
      </h4>
      <div className="p-6 text-lg leading-relaxed relative">
        {narrative}
      </div>
    </div>
  );
} 