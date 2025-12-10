/**
 * ControlPanel Component
 * Dropdowns and analyze button for gap analysis
 */
import { BookOpen, BarChart3, Loader2 } from 'lucide-react';
import Dropdown from '../common/Dropdown';

const ControlPanel = ({
    programs,
    careers,
    selectedProgram,
    selectedCareer,
    setSelectedProgram,
    setSelectedCareer,
    isProgramOpen,
    isCareerOpen,
    setIsProgramOpen,
    setIsCareerOpen,
    optionsLoading,
    loading,
    onAnalyze,
    setShowResults
}) => {
    return (
        <div className="bg-white/80 dark:bg-slate-800/40 backdrop-blur-md rounded-2xl shadow-lg shadow-indigo-100/30 dark:shadow-none border border-white dark:border-slate-700/30 p-4 md:p-8 mb-8 transition-all duration-300 hover:shadow-xl hover:shadow-indigo-200/20 dark:hover:shadow-none relative z-30">
            <div className="flex flex-col md:flex-row items-end gap-4">
                {/* Program Dropdown */}
                <Dropdown
                    label="Select Curriculum"
                    icon={BookOpen}
                    options={programs}
                    selected={selectedProgram}
                    onSelect={(program) => {
                        setSelectedProgram(program);
                        setShowResults(false);
                    }}
                    isOpen={isProgramOpen}
                    onToggle={() => {
                        if (!optionsLoading) {
                            setIsProgramOpen(!isProgramOpen);
                            setIsCareerOpen(false);
                        }
                    }}
                    onClose={() => setIsProgramOpen(false)}
                    loading={optionsLoading}
                    placeholder="No curriculum found"
                />

                {/* Career Dropdown */}
                <Dropdown
                    label="Target Career Path"
                    icon={BarChart3}
                    options={careers}
                    selected={selectedCareer}
                    onSelect={(career) => {
                        setSelectedCareer(career);
                        setShowResults(false);
                    }}
                    isOpen={isCareerOpen}
                    onToggle={() => {
                        if (!optionsLoading) {
                            setIsCareerOpen(!isCareerOpen);
                            setIsProgramOpen(false);
                        }
                    }}
                    onClose={() => setIsCareerOpen(false)}
                    loading={optionsLoading}
                    placeholder="No job roles found"
                />

                {/* Analyze Button */}
                <div className="w-full md:w-auto">
                    <button 
                        onClick={onAnalyze}
                        className="w-full md:w-auto px-8 py-4 bg-gradient-to-r from-indigo-500 to-indigo-600 dark:from-indigo-500 dark:to-indigo-600 text-white rounded-xl font-bold shadow-lg shadow-indigo-500/20 dark:shadow-indigo-900/20 hover:from-indigo-600 hover:to-indigo-700 dark:hover:from-indigo-400 dark:hover:to-indigo-500 hover:scale-[1.02] hover:shadow-indigo-500/30 active:scale-95 transition-all duration-200 flex items-center justify-center h-[54px] text-sm md:text-base cursor-pointer"
                        disabled={loading || !selectedProgram || !selectedCareer}
                    >
                        {loading ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin mr-2" />
                                Analyzing...
                            </>
                        ) : 'Run Analysis'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ControlPanel;
