/**
 * Smooth Scroll Utility
 * Custom smooth scroll helper function with controlled timing
 */
export const smoothScroll = (target, duration = 2000) => {
    if (!target) return;
    
    const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - 80;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    let startTime = null;

    const animation = (currentTime) => {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const progress = Math.min(timeElapsed / duration, 1);
        
        // Very gentle easeInOutSine - most natural feeling
        const easeProgress = -(Math.cos(Math.PI * progress) - 1) / 2;
        const run = startPosition + distance * easeProgress;
        
        window.scrollTo(0, run);
        if (progress < 1) requestAnimationFrame(animation);
    };
    
    requestAnimationFrame(animation);
};

export default smoothScroll;
