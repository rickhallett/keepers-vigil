import { useState, useEffect, useRef, useCallback } from 'react';

interface UseTypewriterOptions {
  speed?: number;
  startDelay?: number;
  onComplete?: () => void;
}

export function useTypewriter(
  text: string,
  options: UseTypewriterOptions = {}
) {
  const { speed = 18, startDelay = 0, onComplete } = options;

  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isComplete, setIsComplete] = useState(false);

  const indexRef = useRef(0);
  const timeoutRef = useRef<number | undefined>(undefined);
  const onCompleteRef = useRef(onComplete);

  // Keep onComplete ref updated
  useEffect(() => {
    onCompleteRef.current = onComplete;
  }, [onComplete]);

  useEffect(() => {
    // Reset when text changes
    indexRef.current = 0;
    setDisplayedText('');
    setIsComplete(false);

    if (!text) {
      setIsTyping(false);
      return;
    }

    // Start typing after delay
    const startTimeout = window.setTimeout(() => {
      setIsTyping(true);
    }, startDelay);

    return () => {
      window.clearTimeout(startTimeout);
      if (timeoutRef.current !== undefined) {
        window.clearTimeout(timeoutRef.current);
      }
    };
  }, [text, startDelay]);

  useEffect(() => {
    if (!isTyping || !text) return;

    const typeNextChar = () => {
      if (indexRef.current < text.length) {
        setDisplayedText(text.slice(0, indexRef.current + 1));
        indexRef.current++;

        // Slight variance for natural feel
        const variance = Math.random() * 6 - 3;
        const nextSpeed = Math.max(8, speed + variance);

        // Pause on punctuation
        const char = text[indexRef.current - 1];
        const pauseMultiplier = /[.!?]/.test(char) ? 8 : /[,;:]/.test(char) ? 3 : 1;

        timeoutRef.current = window.setTimeout(typeNextChar, nextSpeed * pauseMultiplier);
      } else {
        setIsTyping(false);
        setIsComplete(true);
        onCompleteRef.current?.();
      }
    };

    typeNextChar();

    return () => {
      if (timeoutRef.current !== undefined) {
        window.clearTimeout(timeoutRef.current);
      }
    };
  }, [isTyping, text, speed]);

  const skipToEnd = useCallback(() => {
    if (timeoutRef.current !== undefined) {
      window.clearTimeout(timeoutRef.current);
    }
    setDisplayedText(text);
    setIsTyping(false);
    setIsComplete(true);
    indexRef.current = text.length;
    onCompleteRef.current?.();
  }, [text]);

  return {
    displayedText,
    isTyping,
    isComplete,
    skipToEnd,
  };
}
