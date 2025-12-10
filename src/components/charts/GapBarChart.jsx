/**
 * GapBarChart Component
 * Bar chart showing gap analysis overview
 */
import { 
    BarChart, 
    Bar, 
    XAxis, 
    YAxis, 
    CartesianGrid, 
    Legend, 
    ResponsiveContainer,
    Tooltip 
} from 'recharts';
import { CustomTooltip } from '../common';

const GapBarChart = ({ results, darkMode }) => {
    const barData = [
        {
            name: 'Skills',
            Matches: results.matchingSkills,
            Gaps: results.missingSkills,
            Total: results.matchingSkills + results.missingSkills
        }
    ];

    return (
        <div className="bg-white/80 dark:bg-slate-800/50 backdrop-blur-md p-4 md:p-6 rounded-2xl shadow-sm border border-white/50 dark:border-slate-700/50 hover:shadow-xl hover:scale-[1.01] transition-all duration-300">
            <h4 className="text-indigo-900 dark:text-slate-200 text-xs md:text-sm font-bold uppercase tracking-wider mb-6 text-center md:text-left">
                Gap Analysis Overview
            </h4>
            <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%" className="outline-none">
                    <BarChart data={barData} layout="horizontal" barSize={45} className="outline-none focus:outline-none">
                        <defs>
                            <linearGradient id="barMatch" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor="#10b981" stopOpacity={0.9}/>
                                <stop offset="100%" stopColor="#047857" stopOpacity={0.9}/>
                            </linearGradient>
                            <linearGradient id="barGap" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor="#f43f5e" stopOpacity={0.9}/>
                                <stop offset="100%" stopColor="#e11d48" stopOpacity={0.9}/>
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={darkMode ? '#334155' : '#e2e8f0'} />
                        <XAxis 
                            dataKey="name" 
                            axisLine={false} 
                            tickLine={false} 
                            hide={true} 
                        />
                        <YAxis 
                            axisLine={false} 
                            tickLine={false} 
                            tick={{fill: darkMode ? '#e0e7ff' : '#312e81', fontSize: 10, fontWeight: 600}} 
                        />
                        <Legend iconType="circle" wrapperStyle={{ paddingTop: '10px', fontSize: '12px', fontWeight: 500 }}/>
                        <Tooltip cursor={false} content={<CustomTooltip />} allowEscapeViewBox={{ x: true, y: true }} wrapperStyle={{ outline: 'none' }} />
                        
                        <Bar dataKey="Matches" name="Matches" fill="url(#barMatch)" radius={[6, 6, 6, 6]} filter="url(#shadow)" />
                        <Bar dataKey="Gaps" name="Missing Gaps" fill="url(#barGap)" radius={[6, 6, 6, 6]} filter="url(#shadow)" />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default GapBarChart;
