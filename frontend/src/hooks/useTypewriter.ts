import { useState, useEffect, useRef, useCallback } from 'react';

interface UseTypewriterOptions {
  speed?: number;
  startDelay?: number;
  onComplete?: () => void;
}

interface TypewriterState {
  displayedText: string;
  isTyping: boolean;
  isComplete: boolean;
  prevText: string;
}

export function useTypewriter(
  text: string,
  options: UseTypewriterOptions = {}
) {
  const { speed = 18, startDelay = 0, onComplete } = options;

  // Store previous text in state to detect changes during render
  // This is React's recommended pattern for adjusting state based on props
  const [state, setState] = useState<TypewriterState>(() => ({
    displayedText: '',
    isTyping: false,
    isComplete: false,
    prevText: text,
  }));

  const indexRef = useRef(0);
  const timeoutRef = useRef<number | undefined>(undefined);
  const onCompleteRef = useRef(onComplete);

  // Detect text change and reset state during render (React recommended pattern)
  // See: https://react.dev/learn/you-might-not-need-an-effect#adjusting-some-state-when-a-prop-changes
  if (text !== state.prevText) {
    // Clear timeout synchronously - safe because we're resetting before any render-dependent logic
    if (timeoutRef.current !== undefined) {
      // eslint-disable-next-line react-hooks/refs
      window.clearTimeout(timeoutRef.current);
      timeoutRef.current = undefined;
    }
    // eslint-disable-next-line react-hooks/refs
    indexRef.current = 0;
    setState({
      displayedText: '',
      isTyping: false,
      isComplete: false,
      prevText: text,
    });
  }

  // Keep onComplete ref updated
  useEffect(() => {
    onCompleteRef.current = onComplete;
  }, [onComplete]);

  // Start typing effect after delay
  useEffect(() => {
    if (!text || state.isTyping || state.isComplete) {
      return;
    }

    const startTimeout = window.setTimeout(() => {
      setState(prev => ({ ...prev, isTyping: true }));
    }, startDelay);

    return () => {
      window.clearTimeout(startTimeout);
    };
  }, [text, startDelay, state.isTyping, state.isComplete]);

  useEffect(() => {
    if (!state.isTyping || !text) return;

    const typeNextChar = () => {
      if (indexRef.current < text.length) {
        const newDisplayed = text.slice(0, indexRef.current + 1);
        setState(prev => ({ ...prev, displayedText: newDisplayed }));
        indexRef.current++;

        // Slight variance for natural feel
        const variance = Math.random() * 6 - 3;
        const nextSpeed = Math.max(8, speed + variance);

        // Pause on punctuation
        const char = text[indexRef.current - 1];
        const pauseMultiplier = /[.!?]/.test(char) ? 8 : /[,;:]/.test(char) ? 3 : 1;

        timeoutRef.current = window.setTimeout(typeNextChar, nextSpeed * pauseMultiplier);
      } else {
        setState(prev => ({ ...prev, isTyping: false, isComplete: true }));
        onCompleteRef.current?.();
      }
    };

    typeNextChar();

    return () => {
      if (timeoutRef.current !== undefined) {
        window.clearTimeout(timeoutRef.current);
      }
    };
  }, [state.isTyping, text, speed]);

  const skipToEnd = useCallback(() => {
    if (timeoutRef.current !== undefined) {
      window.clearTimeout(timeoutRef.current);
    }
    setState(prev => ({
      ...prev,
      displayedText: text,
      isTyping: false,
      isComplete: true,
    }));
    indexRef.current = text.length;
    onCompleteRef.current?.();
  }, [text]);

  return {
    displayedText: state.displayedText,
    isTyping: state.isTyping,
    isComplete: state.isComplete,
    skipToEnd,
  };
}
