/**
 * SkillList Component
 * Displays a list of skills with expand/collapse functionality
 */
import { useState, useEffect, useRef } from 'react';
import { CheckCircle, AlertCircle } from 'lucide-react';
import SkillBadge from './SkillBadge';

const SkillList = ({ 
    title, 
    skills, 
    variant = 'matched',
    showAll,
    onToggle,
    sectionRef
}) => {
    const contentRef = useRef(null);
    const [hasOverflow, setHasOverflow] = useState(false);

    useEffect(() => {
        const checkOverflow = () => {
            if (contentRef.current) {
                const isContentOverflowing = contentRef.current.scrollHeight > 200;
                setHasOverflow(isContentOverflowing);
            }
        };

        // Check after a brief delay to ensure content is rendered
        const timer = setTimeout(checkOverflow, 100);
        window.addEventListener('resize', checkOverflow);
        return () => {
            clearTimeout(timer);
            window.removeEventListener('resize', checkOverflow);
        };
    }, [skills]);
    const isMatched = variant === 'matched';
    const containerClass = isMatched ? '' : 'bg-rose-50/20 dark:bg-rose-900/5';
    const Icon = isMatched ? CheckCircle : AlertCircle;
    const iconClass = isMatched ? 'text-emerald-400/70' : 'text-rose-400/70';
    const badgeClass = isMatched 
        ? 'text-emerald-600 dark:text-emerald-400 bg-emerald-50/50 dark:bg-emerald-900/20 border-emerald-100/50 dark:border-emerald-900/30'
        : 'text-rose-600 dark:text-rose-400 bg-rose-50/50 dark:bg-rose-900/20 border-rose-100/50 dark:border-rose-900/30';
    const buttonHoverClass = isMatched
        ? 'hover:text-emerald-600 hover:border-emerald-300 dark:hover:border-emerald-600'
        : 'hover:text-rose-600 hover:border-rose-300 dark:hover:border-rose-600';

    return (
        <div className={`p-4 md:p-6 ${containerClass}`} ref={sectionRef}>
            <div className="flex items-center gap-2 mb-4">
                <Icon className={`w-4 h-4 ${iconClass}`} />
                <h5 className="font-semibold text-sm md:text-lg text-slate-600 dark:text-slate-300">{title}</h5>
                <span className={`ml-auto text-xs font-semibold px-2 py-1 rounded-full border ${badgeClass}`}>
                    {skills?.length || 0}
                </span>
            </div>
            <div 
                ref={contentRef}
                className="flex flex-wrap gap-2 transition-all duration-500 ease-in-out" 
                style={{ 
                    maxHeight: showAll ? '2000px' : '200px',
                    overflow: 'hidden'
                }}
            >
                {skills && skills.length > 0 ? (
                    skills.map((skill, index) => (
                        <SkillBadge key={index} skill={skill} variant={variant} />
                    ))
                ) : (
                    <span className="text-slate-400 dark:text-slate-500 text-xs italic">None</span>
                )}
            </div>
            {hasOverflow && (
                <button 
                    onClick={onToggle} 
                    className={`mt-4 px-3 py-1.5 bg-slate-50 dark:bg-slate-700/50 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-600/50 rounded-full text-sm md:text-base font-medium transition-all duration-300 cursor-pointer hover:scale-105 hover:shadow-md hover:bg-white dark:hover:bg-slate-600/50 ${buttonHoverClass}`}
                >
                    {showAll ? "Show Less" : "Show More"}
                </button>
            )}
        </div>
    );
};

export default SkillList;
