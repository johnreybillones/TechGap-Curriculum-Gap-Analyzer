/**
 * SkillBadge Component
 * Individual skill badge with hover effects
 */
const SkillBadge = ({ skill, variant = 'matched' }) => {
    const variants = {
        matched: 'border-emerald-100/70 dark:border-emerald-900/30 text-emerald-600/80 dark:text-emerald-400/80 hover:border-emerald-200/80 dark:hover:border-emerald-700/50',
        missing: 'border-rose-100/70 dark:border-rose-900/30 text-rose-600/80 dark:text-rose-400/80 hover:border-rose-200/80 dark:hover:border-rose-700/50'
    };

    return (
        <span 
            className={`px-3 py-1 bg-white dark:bg-slate-800/50 border rounded-full text-xs md:text-base font-medium hover:scale-105 transition-transform cursor-default shadow-sm hover:shadow-md ${variants[variant]}`}
        >
            {skill}
        </span>
    );
};

export default SkillBadge;
