import { memo, useEffect, useRef, useState } from 'react';
import type { NarrativeEntry } from '../hooks/useGameState';
import { useTypewriter } from '../hooks/useTypewriter';
import '../styles/game.css';

interface NarrativeDisplayProps {
  entries: NarrativeEntry[];
  isLoading: boolean;
}

const NarrativeEntryComponent = memo(function NarrativeEntryComponent({
  entry,
  isLatest,
}: {
  entry: NarrativeEntry;
  isLatest: boolean;
}) {
  const shouldTypewrite = isLatest && entry.type === 'narrator';
  const { displayedText, isTyping, skipToEnd } = useTypewriter(
    shouldTypewrite ? entry.text : '',
    { speed: 18 }
  );

  const text = shouldTypewrite ? displayedText : entry.text;

  return (
    <div
      className={`narrative-entry narrative-${entry.type} ${isTyping ? 'typing' : ''}`}
      onClick={isTyping ? skipToEnd : undefined}
    >
      {text.split('\n').map((line, i) => (
        <p key={i}>{line || '\u00A0'}</p>
      ))}
    </div>
  );
});

export function NarrativeDisplay({ entries, isLoading }: NarrativeDisplayProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);

  // Auto-scroll to bottom when new content appears
  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [entries, autoScroll]);

  // Detect manual scroll
  const handleScroll = () => {
    if (!containerRef.current) return;

    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
    setAutoScroll(isAtBottom);
  };

  return (
    <div
      ref={containerRef}
      className="narrative-display"
      onScroll={handleScroll}
    >
      {entries.map((entry, index) => (
        <NarrativeEntryComponent
          key={entry.id}
          entry={entry}
          isLatest={index === entries.length - 1}
        />
      ))}

      {isLoading && (
        <div className="narrative-loading">
          <span className="loading-dots">...</span>
        </div>
      )}
    </div>
  );
}
