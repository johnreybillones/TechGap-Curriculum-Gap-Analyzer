/**
 * SkillDetails Component
 * Container for matched and missing skills lists
 */
import SkillList from './SkillList';

const SkillDetails = ({ 
    results, 
    showAllMatches, 
    showAllGaps, 
    onToggleMatches, 
    onToggleGaps,
    matchedSkillsRef,
    missingSkillsRef
}) => {
    return (
        <div className="bg-white/80 dark:bg-slate-800/50 backdrop-blur-md rounded-2xl shadow-sm border border-white/50 dark:border-slate-700/50 hover:shadow-lg transition-shadow duration-300">
            <div className="bg-slate-50/50 dark:bg-slate-900/30 px-4 py-3 md:px-6 md:py-4 border-b border-slate-100 dark:border-slate-700/50">
                <h4 className="font-bold text-sm md:text-base text-slate-600 dark:text-slate-300">Skill Details</h4>
            </div>
            <div className="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-100 dark:divide-slate-700/50">
                <SkillList
                    title="Matched Skills"
                    skills={results.exact}
                    variant="matched"
                    showAll={showAllMatches}
                    onToggle={onToggleMatches}
                    sectionRef={matchedSkillsRef}
                />
                <SkillList
                    title="Missing Skills"
                    skills={results.gaps}
                    variant="missing"
                    showAll={showAllGaps}
                    onToggle={onToggleGaps}
                    sectionRef={missingSkillsRef}
                />
            </div>
        </div>
    );
};

export default SkillDetails;
