/**
 * MetricsGrid Component
 * Displays the 4 stat cards for analysis results
 */
import { Target, CheckCircle, AlertCircle, BarChart3 } from 'lucide-react';
import { StatCard } from '../common';

const MetricsGrid = ({ results }) => {
    return (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-6 mb-6 md:mb-8">
            <StatCard 
                label="Total Required" 
                value={results.matchingSkills + results.missingSkills} 
                icon={<Target className="w-4 h-4 text-slate-400 dark:text-slate-500" />}
            />
            <StatCard 
                label="Matches Found" 
                value={results.matchingSkills} 
                color="text-emerald-600/90 dark:text-emerald-400/90"
                icon={<CheckCircle className="w-4 h-4 text-emerald-600/80 dark:text-emerald-400/80" />}
            />
            <StatCard 
                label="Critical Gaps" 
                value={results.missingSkills} 
                color="text-rose-500 dark:text-rose-400"
                icon={<AlertCircle className="w-4 h-4 text-rose-500 dark:text-rose-400" />}
            />
            <StatCard 
                label="Job Coverage" 
                value={results.coverage} 
                subtext="of job skills met"
                color="text-indigo-500 dark:text-indigo-400"
                icon={<BarChart3 className="w-4 h-4 text-indigo-500 dark:text-indigo-400" />}
            />
        </div>
    );
};

export default MetricsGrid;
