/**
 * StatCard Component
 * Reusable metric card for displaying statistics
 */
const StatCard = ({ label, value, color = "text-slate-700 dark:text-slate-200", subtext, icon }) => (
    <div className="bg-white/80 dark:bg-slate-800/50 backdrop-blur-md p-3 md:p-5 rounded-2xl shadow-sm border border-white/60 dark:border-slate-700/50 flex flex-col justify-between h-full transition-all duration-500 hover:shadow-xl hover:-translate-y-1 hover:border-indigo-200/60 dark:hover:border-indigo-800/40 hover:shadow-indigo-100/30 dark:hover:shadow-indigo-900/20 group">
        {/* Header */}
        <div className="flex items-center gap-2 mb-2">
            <div className="p-1.5 md:p-2 rounded-lg bg-slate-50 dark:bg-slate-900/50 transition-colors group-hover:bg-indigo-50 dark:group-hover:bg-indigo-900/20">
                {icon}
            </div>
            <h4 className="text-slate-500 dark:text-slate-400 text-[10px] md:text-xs font-bold uppercase tracking-wider truncate leading-tight group-hover:text-indigo-600 dark:group-hover:text-indigo-300 transition-colors">
                {label}
            </h4>
        </div>
        
        {/* Body */}
        <div className="mt-auto">
            <div className={`text-2xl md:text-3xl font-extrabold ${color} leading-none tracking-tight drop-shadow-sm`}>
                {value}
            </div>
            <p className={`text-[9px] md:text-xs mt-1 truncate ${subtext ? 'text-slate-400 dark:text-slate-500' : 'text-transparent select-none'}`}>
                {subtext || "spacer"}
            </p>
        </div>
    </div>
);

export default StatCard;
