import { useState, useEffect } from 'react';

export function useKeyboardVisibility() {
  const [isKeyboardVisible, setIsKeyboardVisible] = useState(false);

  useEffect(() => {
    // Only run on mobile devices with visualViewport support
    if (typeof window === 'undefined' || !('visualViewport' in window)) {
      return;
    }

    const viewport = window.visualViewport;
    if (!viewport) return;

    const handleResize = () => {
      // Keyboard is likely visible if viewport height is significantly less than window height
      const heightDiff = window.innerHeight - viewport.height;
      setIsKeyboardVisible(heightDiff > 150);
    };

    viewport.addEventListener('resize', handleResize);
    viewport.addEventListener('scroll', handleResize);

    return () => {
      viewport.removeEventListener('resize', handleResize);
      viewport.removeEventListener('scroll', handleResize);
    };
  }, []);

  return isKeyboardVisible;
}
