/**
 * TechGap Curriculum Gap Analyzer
 * Main Application Component
 * 
 * This is the root component that orchestrates the curriculum gap analysis tool.
 * It uses modular components and custom hooks for clean separation of concerns.
 */
import { Header, Footer, Background } from './components/layout';
import { ControlPanel, MetricsGrid, AIRecommendations, SkillDetails } from './components/analyzer';
import { ChartsSection } from './components/charts';
import { useAnalysis, useOptions, useDarkMode } from './hooks';

export default function CurriculumGapAnalyzer() {
    // Dark mode management
    const { darkMode, setDarkMode } = useDarkMode();

    // Options management (programs, careers, dropdowns)
    const {
        programs,
        careers,
        selectedProgram,
        setSelectedProgram,
        selectedCareer,
        setSelectedCareer,
        isProgramOpen,
        setIsProgramOpen,
        isCareerOpen,
        setIsCareerOpen,
        loading: optionsLoading,
        error: optionsError
    } = useOptions();

    // Analysis state and actions
    const {
        showResults,
        setShowResults,
        results,
        loading,
        error,
        recommendation,
        recLoading,
        isAiOpen,
        setIsAiOpen,
        showAllGaps,
        showAllMatches,
        summaryRef,
        matchedSkillsRef,
        missingSkillsRef,
        handleAnalyze,
        handleToggleMatches,
        handleToggleGaps
    } = useAnalysis();

    // Wrapper for analyze function to pass selected options
    const onAnalyze = () => {
        handleAnalyze(selectedProgram, selectedCareer);
    };

    return (
        <div className="min-h-screen font-sans text-gray-900 dark:text-slate-300 relative selection:bg-indigo-100 dark:selection:bg-indigo-900/30 transition-colors duration-300">
            <Background />
            
            <Header darkMode={darkMode} setDarkMode={setDarkMode} />

            <main className="max-w-6xl mx-auto px-3 md:px-6 py-6 md:py-8 relative z-10">
                {/* Title Section */}
                <div className="text-center mb-8 md:mb-12 mt-4 animate-in fade-in slide-in-from-bottom-4 duration-700">
                    <h2 className="text-4xl md:text-6xl font-extrabold text-slate-800 dark:text-slate-100 mb-4 tracking-tight drop-shadow-sm">
                        Curriculum Gap Analyzer
                    </h2>
                    <p className="text-slate-500 dark:text-slate-400 text-sm md:text-lg mb-2 max-w-2xl mx-auto px-4 leading-relaxed font-medium">
                        Identify critical skill gaps by comparing your course content against real-time industry job market standards.
                    </p>
                </div>

                {/* Control Panel */}
                <ControlPanel
                    programs={programs}
                    careers={careers}
                    selectedProgram={selectedProgram}
                    selectedCareer={selectedCareer}
                    setSelectedProgram={setSelectedProgram}
                    setSelectedCareer={setSelectedCareer}
                    isProgramOpen={isProgramOpen}
                    isCareerOpen={isCareerOpen}
                    setIsProgramOpen={setIsProgramOpen}
                    setIsCareerOpen={setIsCareerOpen}
                    optionsLoading={optionsLoading}
                    loading={loading}
                    onAnalyze={onAnalyze}
                    setShowResults={setShowResults}
                />

                {/* Scroll anchor */}
                <div ref={summaryRef}></div>

                {/* Results Section */}
                <div className="relative z-10">
                    {/* Error Messages */}
                    {optionsError && (
                        <div className="text-red-500 mb-4 bg-red-50 p-4 rounded-xl border border-red-200 animate-in fade-in">
                            {optionsError}
                        </div>
                    )}
                    {error && (
                        <div className="text-red-500 mb-4 bg-red-50 p-4 rounded-xl border border-red-200 animate-in fade-in">
                            {error}
                        </div>
                    )}
                    
                    {/* Analysis Results */}
                    {showResults && results && (
                        <div className="animate-in fade-in slide-in-from-bottom-8 duration-700 pb-10">
                            {/* 1. Metrics Grid */}
                            <MetricsGrid results={results} />

                            {/* 2. Charts Section */}
                            <ChartsSection results={results} darkMode={darkMode} />

                            {/* 3. AI Recommendations */}
                            <AIRecommendations
                                isOpen={isAiOpen}
                                setIsOpen={setIsAiOpen}
                                loading={recLoading}
                                recommendation={recommendation}
                            />

                            {/* 4. Skill Details */}
                            <SkillDetails
                                results={results}
                                showAllMatches={showAllMatches}
                                showAllGaps={showAllGaps}
                                onToggleMatches={handleToggleMatches}
                                onToggleGaps={handleToggleGaps}
                                matchedSkillsRef={matchedSkillsRef}
                                missingSkillsRef={missingSkillsRef}
                            />
                        </div>
                    )}
                </div>
            </main>

            <Footer />
        </div>
    );
}
