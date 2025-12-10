/**
 * Custom Tooltip Component for Recharts
 */
const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-sm p-3 border border-indigo-50 dark:border-slate-700 rounded-xl shadow-xl shadow-indigo-100/20 dark:shadow-none outline-none">
                <p className="font-bold text-indigo-900 dark:text-indigo-100 text-sm mb-2 text-left">{label}</p>
                <div className="flex flex-col items-start gap-1">
                    {payload.map((entry, index) => (
                        <p key={index} style={{ color: entry.color }} className="font-medium flex items-center gap-2 text-xs md:text-sm whitespace-nowrap">
                            <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: entry.color }}></span>
                            {entry.name}: {entry.value}
                        </p>
                    ))}
                </div>
            </div>
        );
    }
    return null;
};

export default CustomTooltip;
