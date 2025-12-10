/**
 * RelevancePieChart Component
 * Pie chart showing curriculum relevance
 */
import { 
    PieChart, 
    Pie, 
    Cell, 
    Legend, 
    ResponsiveContainer,
    Tooltip 
} from 'recharts';
import { CustomTooltip } from '../common';

const RelevancePieChart = ({ results }) => {
    const pieData = [
        { name: 'Relevant', value: results.matchingSkills, color: 'url(#colorRelevant)' }, 
        { name: 'Others', value: results.irrelevantSkills || 0, color: 'url(#colorOthers)' } 
    ];

    return (
        <div className="bg-white/80 dark:bg-slate-800/50 backdrop-blur-md p-4 md:p-6 rounded-2xl shadow-sm border border-white/50 dark:border-slate-700/50 hover:shadow-xl hover:scale-[1.01] transition-all duration-300">
            <h4 className="text-indigo-900 dark:text-slate-200 text-xs md:text-sm font-bold uppercase tracking-wider mb-6 text-center md:text-left">
                Curriculum Relevance
            </h4>
            <div className="h-64 w-full relative">
                {/* Center Text */}
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none mb-4">
                    <div className="text-center"> 
                        <p className="text-3xl md:text-4xl font-extrabold text-indigo-900 dark:text-slate-200 drop-shadow-sm">
                            {results.relevance}
                        </p>
                        <p className="text-xs text-indigo-900/70 dark:text-slate-400 font-medium mt-1">Relevant</p>
                    </div>
                </div>

                <ResponsiveContainer width="100%" height="100%" className="outline-none">
                    <PieChart className="outline-none focus:outline-none">
                        <defs>
                            <linearGradient id="colorRelevant" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                                <stop offset="95%" stopColor="#059669" stopOpacity={0.9}/>
                            </linearGradient>
                            <linearGradient id="colorOthers" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#94a3b8" stopOpacity={0.4}/>
                                <stop offset="95%" stopColor="#64748b" stopOpacity={0.7}/>
                            </linearGradient>
                            <filter id="shadow" height="130%">
                                <feDropShadow dx="0" dy="3" stdDeviation="3" floodColor="#000" floodOpacity="0.1"/>
                            </filter>
                        </defs>
                        <Pie
                            data={pieData}
                            cx="50%"
                            cy="50%"
                            innerRadius="65%" 
                            outerRadius="85%"
                            paddingAngle={4}
                            dataKey="value"
                            stroke="none"
                            cornerRadius={6} 
                        >
                            {pieData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} filter="url(#shadow)" />
                            ))}
                        </Pie>
                        <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '12px', fontWeight: 500 }} />
                        <Tooltip content={<CustomTooltip />} allowEscapeViewBox={{ x: true, y: true }} wrapperStyle={{ outline: 'none' }} />
                    </PieChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default RelevancePieChart;
