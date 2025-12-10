import React, { useEffect, useState, useRef } from 'react';
import ReactMarkdown from 'react-markdown'; 
import { 
    ChevronDown, 
    BarChart3, 
    CheckCircle, 
    AlertCircle, 
    BookOpen, 
    Target, 
    Sparkles, 
    Loader2,
    Sun,
    Moon
} from 'lucide-react';
import { 
    PieChart, 
    Pie, 
    Cell, 
    BarChart, 
    Bar, 
    XAxis, 
    YAxis, 
    CartesianGrid, 
    Legend, 
    ResponsiveContainer,
    Tooltip 
} from 'recharts';
import logoPng from './assets/logo.png';

// --- TECHGAP LOGO ---
const TechGapLogo = ({ className = "w-8 h-8" }) => (
    <img src={logoPng} alt="TechGap Logo" className={`${className} object-contain`} />
);

// Custom Smooth Scroll Helper
const smoothScroll = (target, duration) => {
    if (!target) return;
    const targetPosition = target.getBoundingClientRect().top + window.pageYOffset;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition - 80; 
    let startTime = null;

    const animation = (currentTime) => {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const ease = (t, b, c, d) => {
            t /= d / 2;
            if (t < 1) return c / 2 * t * t + b;
            t--;
            return -c / 2 * (t * (t - 2) - 1) + b;
        };
        const run = ease(timeElapsed, startPosition, distance, duration);
        window.scrollTo(0, run);
        if (timeElapsed < duration) requestAnimationFrame(animation);
    };
    requestAnimationFrame(animation);
};

export default function CurriculumGapAnalyzer() {

    const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
    const [showResults, setShowResults] = useState(false);
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    
    // --- AI Recommendation State ---
    const [recommendation, setRecommendation] = useState('');
    const [recLoading, setRecLoading] = useState(false);
    const [isAiOpen, setIsAiOpen] = useState(true); 

    // --- Skill List Truncation State ---
    const [showAllGaps, setShowAllGaps] = useState(false);
    const [showAllMatches, setShowAllMatches] = useState(false);

    const [error, setError] = useState('');
    const [programs, setPrograms] = useState([]);
    const [careers, setCareers] = useState([]);
    const [selectedProgram, setSelectedProgram] = useState(null);
    const [selectedCareer, setSelectedCareer] = useState(null);
    const [isProgramOpen, setIsProgramOpen] = useState(false);
    const [isCareerOpen, setIsCareerOpen] = useState(false);
    const [optionsLoading, setOptionsLoading] = useState(true);
    const [optionsError, setOptionsError] = useState('');
    
    // --- Dark Mode State ---
    const [darkMode, setDarkMode] = useState(() => {
        if (typeof window !== 'undefined') {
            const savedTheme = localStorage.getItem('theme');
            return savedTheme === 'dark';
        }
        return false;
    });

    const summaryRef = useRef(null);

    // --- Dark Mode Effect ---
    useEffect(() => {
        if (darkMode) {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    }, [darkMode]);

    useEffect(() => {
        const loadOptions = async () => {
            try {
                setOptionsError('');
                setOptionsLoading(true);
                const optionsRes = await fetch(`${API_BASE}/api/options`);
                const optionsCt = optionsRes.headers.get('content-type') || '';
                let mappedCurr = [];
                let mappedJobs = [];

                if (optionsRes.ok && optionsCt.includes('application/json')) {
                    const opts = await optionsRes.json();
                    mappedCurr = (opts.curricula || []).filter((c) => c.id && c.label);
                    mappedJobs = (opts.jobs || []).filter((j) => j.id && j.label);
                }

                setPrograms(mappedCurr);
                setCareers(mappedJobs);
                if (mappedCurr.length > 0) setSelectedProgram(mappedCurr[0]);
                if (mappedJobs.length > 0) setSelectedCareer(mappedJobs[0]);
            } catch (err) {
                setOptionsError(err.message);
            } finally {
                setOptionsLoading(false);
            }
        };
        loadOptions();
    }, []);


    const handleAnalyze = async () => {
        setLoading(true);
        setRecLoading(true);
        setRecommendation('');
        setError('');
        setShowResults(false);
        setIsAiOpen(true); 
        setShowAllGaps(false); 
        setShowAllMatches(false);
        
        try {
            const response = await fetch(`${API_BASE}/api/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    curriculum_id: selectedProgram?.id,
                    job_id: selectedCareer?.id
                })
            });
            
            if (!response.ok) throw new Error(`Failed to fetch analysis (${response.status})`);
            
            const data = await response.json();
            setResults(data);
            setShowResults(true);

            setTimeout(() => {
                smoothScroll(summaryRef.current, 2000);
            }, 100);

            setLoading(false);

            const aiResponse = await fetch(`${API_BASE}/api/recommend`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    job_title: selectedCareer?.label,
                    curriculum_title: selectedProgram?.label,
                    missing_skills: data.gaps,
                    coverage_score: data.coverage_score
                })
            });

            if (aiResponse.ok) {
                const aiData = await aiResponse.json();
                setRecommendation(aiData.recommendation);
            } else {
                setRecommendation("Could not fetch AI insights.");
            }

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
            setRecLoading(false);
        }
    };

    const pieData = results ? [
        { name: 'Relevant', value: results.matchingSkills, color: 'url(#colorRelevant)' }, 
        { name: 'Others', value: results.irrelevantSkills || 0, color: 'url(#colorOthers)' } 
    ] : [];

    const barData = results ? [
        {
            name: 'Skills',
            Matches: results.matchingSkills,
            Gaps: results.missingSkills,
            Total: results.matchingSkills + results.missingSkills
        }
    ] : [];

    const getVisibleSkills = (skills, showAll) => {
        if (!skills) return [];
        if (showAll) return skills;
        return skills.slice(0, 15); 
    };

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-sm p-3 border border-indigo-50 dark:border-slate-700 rounded-xl shadow-xl shadow-indigo-100/20 dark:shadow-none outline-none">
                    <p className="font-bold text-indigo-900 dark:text-indigo-100 text-sm mb-2">{label}</p>
                    {payload.map((entry, index) => (
                        <p key={index} style={{ color: entry.color }} className="font-medium flex items-center gap-2 text-xs md:text-sm">
                            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }}></span>
                            {entry.name}: {entry.value}
                        </p>
                    ))}
                </div>
            );
        }
        return null;
    };

    return (
        // BACKGROUND FIX: Stronger Gradient + Grid Pattern
        <div className="min-h-screen font-sans text-gray-900 dark:text-slate-300 relative selection:bg-indigo-100 dark:selection:bg-indigo-900/30 transition-colors duration-300">
             {/* Fixed Background Layer */}
             <div className="fixed inset-0 -z-10 h-full w-full bg-[radial-gradient(#cbd5e1_1px,transparent_1px)] dark:bg-[radial-gradient(#334155_1px,transparent_1px)] [background-size:24px_24px] [mask-image:radial-gradient(ellipse_60%_60%_at_50%_50%,#000_70%,transparent_100%)] opacity-100 dark:opacity-20"></div>
             <div className="fixed inset-0 -z-20 h-full w-full bg-slate-50 dark:bg-slate-900 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-100/50 via-slate-50 to-slate-50 dark:from-slate-800/50 dark:via-slate-900 dark:to-slate-900 transition-colors duration-300"></div>

            {/* Header */}
            <header className="bg-white/70 dark:bg-slate-900/50 backdrop-blur-xl border-b border-slate-100 dark:border-slate-800/30 px-4 md:px-6 py-3 sticky top-0 z-40 shadow-sm transition-all duration-300">
                <div className="max-w-6xl mx-auto flex items-center gap-2">
                    <div className="w-8 h-8 flex items-center justify-center transform hover:scale-105 transition-transform duration-300">
                        <TechGapLogo className="w-8 h-8 drop-shadow-md" />
                    </div>
                    <h1 className="text-lg md:text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-700 to-indigo-600 dark:from-slate-200 dark:to-indigo-300 tracking-tight">TechGap</h1>
                    
                    {/* Dark Mode Toggle Slider */}
                    <button 
                        onClick={() => setDarkMode(!darkMode)}
                        className={`ml-auto relative w-16 h-8 rounded-full transition-colors duration-500 focus:outline-none shadow-inner border border-slate-200 dark:border-slate-700 cursor-pointer z-50 ${darkMode ? 'bg-slate-800' : 'bg-indigo-50'}`}
                        aria-label="Toggle Dark Mode"
                    >
                        <div className={`absolute top-1 left-1 w-6 h-6 rounded-full shadow-md transform transition-transform duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)] flex items-center justify-center border ${darkMode ? 'translate-x-8 bg-slate-900 border-slate-700' : 'translate-x-0 bg-white border-white'}`}>
                            {darkMode ? (
                                <Moon className="w-3.5 h-3.5 text-indigo-400" />
                            ) : (
                                <Sun className="w-4 h-4 text-amber-500" />
                            )}
                        </div>
                    </button>
                </div>
            </header>

            {/* Main Content */}
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
                {/* DROPDOWN FIX: Added z-30 to this container to keep it above results */}
                <div className="bg-white/80 dark:bg-slate-800/40 backdrop-blur-md rounded-2xl shadow-lg shadow-indigo-100/30 dark:shadow-none border border-white dark:border-slate-700/30 p-4 md:p-8 mb-8 transition-all duration-300 hover:shadow-xl hover:shadow-indigo-200/20 dark:hover:shadow-none relative z-30">
                    <div className="flex flex-col md:flex-row items-end gap-4">
                        {/* Program Dropdown */}
                        <div className="w-full md:flex-1 relative group">
                            <label className="block text-xs md:text-sm font-bold text-slate-500 dark:text-slate-400 uppercase mb-2 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors ml-1">Select Curriculum</label>
                            <button
                                onClick={() => {
                                    if (optionsLoading) return;
                                    setIsProgramOpen(!isProgramOpen);
                                    setIsCareerOpen(false);
                                }}
                                className="w-full flex items-center justify-between px-4 py-4 bg-slate-50/80 dark:bg-slate-900/30 border border-slate-200 dark:border-slate-700/50 rounded-xl hover:border-indigo-500 dark:hover:border-indigo-500/50 hover:bg-white dark:hover:bg-slate-800/50 focus:outline-none focus:ring-4 focus:ring-indigo-100 dark:focus:ring-indigo-900/20 transition-all text-left disabled:opacity-60 shadow-sm group-hover:shadow-md cursor-pointer"
                                disabled={optionsLoading || programs.length === 0}
                            >
                                <div className="flex items-center gap-3 overflow-hidden">
                                    <BookOpen className="w-5 h-5 text-indigo-500 dark:text-indigo-400 flex-shrink-0" />
                                    <span className="text-slate-700 dark:text-slate-200 font-bold truncate text-sm md:text-base">
                                        {selectedProgram ? selectedProgram.label : optionsLoading ? 'Loading...' : 'No curriculum found'}
                                    </span>
                                </div>
                                <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform duration-300 ${isProgramOpen ? 'rotate-180 text-indigo-500 dark:text-indigo-400' : ''}`} />
                            </button>
                            
                            {/* DROPDOWN FIX: Added z-50 to the absolute menu */}
                            <div className={`absolute z-50 w-full mt-2 bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700/50 rounded-xl shadow-2xl overflow-hidden transition-all duration-200 origin-top ${isProgramOpen ? 'opacity-100 scale-100 translate-y-0' : 'opacity-0 scale-95 -translate-y-2 pointer-events-none'}`}>
                                <div className="max-h-64 overflow-auto py-1 scrollbar-thin scrollbar-thumb-indigo-100 dark:scrollbar-thumb-indigo-900 scrollbar-track-transparent">
                                    {programs.map((program) => (
                                        <button
                                            key={program.id}
                                            onClick={() => {
                                                setSelectedProgram(program);
                                                setIsProgramOpen(false);
                                                setShowResults(false);
                                            }}
                                            className="w-full text-left px-4 py-3 hover:bg-indigo-50 dark:hover:bg-slate-700/30 transition-colors flex items-center gap-3 border-b border-slate-50 dark:border-slate-700/30 last:border-0"
                                        >
                                            <span className={`block truncate text-sm ${selectedProgram?.id === program.id ? 'text-indigo-600 dark:text-indigo-400 font-bold' : 'text-slate-600 dark:text-slate-300'}`}>
                                                {program.label}
                                            </span>
                                            {selectedProgram?.id === program.id && <CheckCircle className="w-4 h-4 text-indigo-600 dark:text-indigo-400 ml-auto" />}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Career Dropdown */}
                        <div className="w-full md:flex-1 relative group">
                            <label className="block text-xs md:text-sm font-bold text-slate-500 dark:text-slate-400 uppercase mb-2 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors ml-1">Target Career Path</label>
                            <button
                                onClick={() => {
                                    if (optionsLoading) return;
                                    setIsCareerOpen(!isCareerOpen);
                                    setIsProgramOpen(false);
                                }}
                                className="w-full flex items-center justify-between px-4 py-4 bg-slate-50/80 dark:bg-slate-900/30 border border-slate-200 dark:border-slate-700/50 rounded-xl hover:border-indigo-500 dark:hover:border-indigo-500/50 hover:bg-white dark:hover:bg-slate-800/50 focus:outline-none focus:ring-4 focus:ring-indigo-100 dark:focus:ring-indigo-900/20 transition-all text-left disabled:opacity-60 shadow-sm group-hover:shadow-md cursor-pointer"
                                disabled={optionsLoading || careers.length === 0}
                            >
                                <div className="flex items-center gap-3 overflow-hidden">
                                    <BarChart3 className="w-5 h-5 text-indigo-500 dark:text-indigo-400 flex-shrink-0" />
                                    <span className="text-slate-700 dark:text-slate-200 font-bold truncate text-sm md:text-base">
                                        {selectedCareer ? selectedCareer.label : optionsLoading ? 'Loading...' : 'No job roles found'}
                                    </span>
                                </div>
                                <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform duration-300 ${isCareerOpen ? 'rotate-180 text-indigo-500 dark:text-indigo-400' : ''}`} />
                            </button>
                            
                            {/* DROPDOWN FIX: Added z-50 */}
                            <div className={`absolute z-50 w-full mt-2 bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700/50 rounded-xl shadow-2xl overflow-hidden transition-all duration-200 origin-top ${isCareerOpen ? 'opacity-100 scale-100 translate-y-0' : 'opacity-0 scale-95 -translate-y-2 pointer-events-none'}`}>
                                <div className="max-h-64 overflow-y-auto py-1 scrollbar-thin scrollbar-thumb-indigo-100 dark:scrollbar-thumb-indigo-900 scrollbar-track-transparent">
                                    {careers.map((career) => (
                                        <button
                                            key={career.id}
                                            onClick={() => {
                                                setSelectedCareer(career);
                                                setIsCareerOpen(false);
                                                setShowResults(false);
                                            }}
                                            className="w-full text-left px-4 py-3 hover:bg-indigo-50 dark:hover:bg-slate-700/30 transition-colors flex items-center gap-3 border-b border-slate-50 dark:border-slate-700/30 last:border-0"
                                        >
                                            <span className={`block truncate text-sm ${selectedCareer?.id === career.id ? 'text-indigo-600 dark:text-indigo-400 font-bold' : 'text-slate-600 dark:text-slate-300'}`}>
                                                {career.label}
                                            </span>
                                            {selectedCareer?.id === career.id && <CheckCircle className="w-4 h-4 text-indigo-600 dark:text-indigo-400 ml-auto" />}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Analyze Button */}
                        <div className="w-full md:w-auto">
                            <button 
                                onClick={handleAnalyze}
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

                <div ref={summaryRef}></div>

                {/* Results Section */}
                {/* Added relative z-10 to ensure it sits below the dropdown */}
                <div className="relative z-10">
                    {optionsError && <div className="text-red-500 mb-4 bg-red-50 p-4 rounded-xl border border-red-200 animate-in fade-in">{optionsError}</div>}
                    {error && <div className="text-red-500 mb-4 bg-red-50 p-4 rounded-xl border border-red-200 animate-in fade-in">{error}</div>}
                    
                    {showResults && results && (
                        <div className="animate-in fade-in slide-in-from-bottom-8 duration-700 pb-10">
                            
                            {/* 1. METRICS GRID */}
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

                            {/* AI Section */}
                            <div className="bg-white/80 dark:bg-slate-800/50 backdrop-blur-md rounded-2xl shadow-sm border border-indigo-50 dark:border-slate-700/50 mb-6 md:mb-8 relative overflow-hidden transition-all duration-300 hover:shadow-md hover:border-indigo-200 dark:hover:border-indigo-900/50 group">
                                <div 
                                    className="flex items-center justify-between p-4 md:p-6 cursor-pointer select-none hover:bg-indigo-50/30 dark:hover:bg-indigo-900/10 transition-colors duration-300"
                                    onClick={() => setIsAiOpen(!isAiOpen)}
                                >
                                    <div className="flex items-center gap-3 relative z-10">
                                        <div className="p-2 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-lg shadow-lg shadow-indigo-500/20 group-hover:scale-110 transition-transform duration-300">
                                            <Sparkles className="w-4 h-4 text-white" />
                                        </div>
                                        <h3 className="text-sm md:text-xl font-bold text-indigo-900 dark:text-slate-200">AI Recommendations</h3>
                                    </div>
                                    <div className={`text-indigo-400 transition-transform duration-300 ${isAiOpen ? 'rotate-180' : ''}`}>
                                        <ChevronDown className="w-5 h-5"/>
                                    </div>
                                </div>
                                
                                <div className={`grid transition-all duration-300 ease-in-out ${isAiOpen ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'}`}>
                                    <div className="overflow-hidden">
                                        <div className="px-4 pb-4 md:px-6 md:pb-6">
                                            {recLoading ? (
                                                <div className="flex items-center gap-3 text-indigo-600 dark:text-indigo-400 py-6 animate-pulse bg-indigo-50/50 dark:bg-indigo-900/10 rounded-xl p-4">
                                                    <Loader2 className="w-5 h-5 animate-spin" />
                                                    <span className="text-sm font-medium">Analyzing curriculum gaps...</span>
                                                </div>
                                            ) : recommendation ? (
                                                <div className="prose prose-sm md:prose-base prose-indigo max-w-none text-slate-700 dark:text-slate-300 bg-indigo-50/30 dark:bg-indigo-900/10 p-5 rounded-xl border border-indigo-50 dark:border-slate-700/50 shadow-inner dark:shadow-none">
                                                    <ReactMarkdown components={{
                                                            ul: ({ node, ...props }) => <ul className="list-disc pl-5 space-y-2" {...props} />,
                                                            ol: ({ node, ...props }) => <ol className="list-decimal pl-5 space-y-2" {...props} />,
                                                            li: ({ node, ...props }) => <li className="text-slate-700 dark:text-slate-300" {...props} />,
                                                            p: ({ node, ...props }) => <p className="text-slate-700 dark:text-slate-300 leading-relaxed" {...props} />,
                                                            h2: ({ node, ...props }) => <h2 className="text-xl font-bold text-indigo-900 dark:text-indigo-200 mt-4" {...props} />,
                                                            h3: ({ node, ...props }) => <h3 className="text-lg font-semibold text-indigo-900 dark:text-indigo-200 mt-3" {...props} />,
                                                            strong: ({ node, ...props }) => <strong className="text-indigo-900 dark:text-indigo-200 font-bold" {...props} />,
                                                    }}>
                                                        {recommendation}
                                                    </ReactMarkdown>
                                                </div>
                                            ) : (
                                                <p className="text-indigo-900/60 dark:text-indigo-200/60 text-sm italic p-4">Waiting for AI insights...</p>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* 2. CHARTS SECTION (ENHANCED) */}
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6 mb-6 md:mb-8">
                                
                                {/* Chart A: Pie Chart */}
                                <div className="bg-white/80 dark:bg-slate-800/50 backdrop-blur-md p-4 md:p-6 rounded-2xl shadow-sm border border-white/50 dark:border-slate-700/50 hover:shadow-xl hover:scale-[1.01] transition-all duration-300">
                                    <h4 className="text-indigo-900 dark:text-slate-200 text-xs md:text-sm font-bold uppercase tracking-wider mb-6 text-center md:text-left">
                                        Curriculum Relevance
                                    </h4>
                                    <div className="h-64 w-full relative">
                                        {/* Center Text - Rendered first so it sits behind the chart/tooltip */}
                                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none mb-4">
                                            <div className="text-center"> 
                                                <p className="text-3xl md:text-4xl font-extrabold text-indigo-900 dark:text-slate-200 drop-shadow-sm">{results.relevance}</p>
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
                                                {/* TOOLTIP FIX: Added allowEscapeViewBox and outline-none */}
                                                <Tooltip content={<CustomTooltip />} allowEscapeViewBox={{ x: true, y: true }} wrapperStyle={{ outline: 'none' }} />
                                            </PieChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>

                                {/* Chart B: Bar Chart */}
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
                                                {/* TOOLTIP FIX: Added allowEscapeViewBox and outline-none */}
                                                <Tooltip cursor={false} content={<CustomTooltip />} allowEscapeViewBox={{ x: true, y: true }} wrapperStyle={{ outline: 'none' }} />
                                                
                                                <Bar dataKey="Matches" name="Matches" fill="url(#barMatch)" radius={[6, 6, 6, 6]} filter="url(#shadow)" />
                                                <Bar dataKey="Gaps" name="Missing Gaps" fill="url(#barGap)" radius={[6, 6, 6, 6]} filter="url(#shadow)" />
                                            </BarChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>
                            </div>

                            {/* 3. Skill Lists */}
                            <div className="bg-white/80 dark:bg-slate-800/50 backdrop-blur-md rounded-2xl shadow-sm border border-white/50 dark:border-slate-700/50 overflow-hidden hover:shadow-lg transition-shadow duration-300">
                                <div className="bg-slate-50/50 dark:bg-slate-900/30 px-4 py-3 md:px-6 md:py-4 border-b border-slate-100 dark:border-slate-700/50">
                                    <h4 className="font-bold text-sm md:text-base text-indigo-900 dark:text-slate-200">Skill Details</h4>
                                </div>
                                <div className="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-100 dark:divide-slate-700/50">
                                    {/* Matched */}
                                    <div className="p-4 md:p-6">
                                        <div className="flex items-center gap-2 mb-4">
                                            <CheckCircle className="w-4 h-4 text-emerald-500/90" />
                                            <h5 className="font-bold text-sm md:text-lg text-slate-700 dark:text-slate-200">Matched Skills</h5>
                                            <span className="ml-auto text-xs font-bold text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-900/30 px-2 py-1 rounded-full border border-emerald-100 dark:border-emerald-900/50">
                                                {results.exact?.length || 0}
                                            </span>
                                        </div>
                                        <div className="flex flex-wrap gap-2">
                                            {results.exact && results.exact.length > 0 ? (
                                                <>
                                                    {getVisibleSkills(results.exact, showAllMatches).map((skill, index) => (
                                                        <span key={index} className="px-3 py-1 bg-white dark:bg-slate-800/50 border border-emerald-100 dark:border-emerald-900/50 text-emerald-700/90 dark:text-emerald-300/90 rounded-full text-xs md:text-base font-medium hover:scale-105 transition-transform cursor-default shadow-sm hover:shadow-md hover:border-emerald-200 dark:hover:border-emerald-700">
                                                            {skill}
                                                        </span>
                                                    ))}
                                                    {results.exact.length > 15 && (
                                                        <button onClick={() => setShowAllMatches(!showAllMatches)} className="px-3 py-1 bg-slate-50 dark:bg-slate-700/50 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-600/50 rounded-full text-xs md:text-base font-medium hover:text-emerald-600 hover:border-emerald-300 dark:hover:border-emerald-600 transition-colors">
                                                            {showAllMatches ? "Less" : `+${results.exact.length - 15}`}
                                                        </button>
                                                    )}
                                                </>
                                            ) : <span className="text-slate-400 dark:text-slate-500 text-xs italic">None</span>}
                                        </div>
                                    </div>

                                    {/* Gaps */}
                                    <div className="p-4 md:p-6 bg-rose-50/30 dark:bg-rose-900/10">
                                        <div className="flex items-center gap-2 mb-4">
                                            <AlertCircle className="w-4 h-4 text-rose-500" />
                                            <h5 className="font-bold text-sm md:text-lg text-slate-700 dark:text-slate-200">Missing Skills</h5>
                                            <span className="ml-auto text-xs font-bold text-rose-700 dark:text-rose-300 bg-rose-50 dark:bg-rose-900/30 px-2 py-1 rounded-full border border-rose-100 dark:border-rose-900/50">
                                                {results.gaps?.length || 0}
                                            </span>
                                        </div>
                                        <div className="flex flex-wrap gap-2">
                                            {results.gaps && results.gaps.length > 0 ? (
                                                <>
                                                    {getVisibleSkills(results.gaps, showAllGaps).map((skill, index) => (
                                                        <span key={index} className="px-3 py-1 bg-white dark:bg-slate-800/50 border border-rose-100 dark:border-rose-900/50 text-rose-700 dark:text-rose-300 rounded-full text-xs md:text-base font-medium hover:scale-105 transition-transform cursor-default shadow-sm hover:shadow-md hover:border-rose-200 dark:hover:border-rose-700">
                                                            {skill}
                                                        </span>
                                                    ))}
                                                    {results.gaps.length > 15 && (
                                                        <button onClick={() => setShowAllGaps(!showAllGaps)} className="px-3 py-1 bg-slate-50 dark:bg-slate-700/50 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-600/50 rounded-full text-xs md:text-base font-medium hover:text-rose-600 hover:border-rose-300 dark:hover:border-rose-600 transition-colors">
                                                            {showAllGaps ? "Less" : `+${results.gaps.length - 15}`}
                                                        </button>
                                                    )}
                                                </>
                                            ) : <span className="text-slate-400 dark:text-slate-500 text-xs italic">None</span>}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </main>

            {/* Footer */}
            <footer className="py-4 text-center text-slate-400 dark:text-slate-600 text-xs md:text-sm relative z-0">
                <p>&copy; {new Date().getFullYear()} Evalrey. All rights reserved.</p>
            </footer>
        </div>
    );
}

// METRIC CARD COMPONENT
const StatCard = ({ label, value, color = "text-slate-700 dark:text-slate-200", subtext, icon }) => (
  <div className="bg-white/80 dark:bg-slate-800/50 backdrop-blur-md p-3 md:p-5 rounded-2xl shadow-sm border border-white/60 dark:border-slate-700/50 flex flex-col justify-between h-full transition-all duration-300 hover:shadow-lg hover:scale-[1.02] hover:border-indigo-100 dark:hover:border-indigo-900/50 group">
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