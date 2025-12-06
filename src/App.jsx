import React, { useEffect, useState, useRef } from 'react';
import { 
    ChevronDown, 
    BarChart3, 
    CheckCircle, 
    AlertCircle, 
    BookOpen, 
    Target, 
    Layers, 
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
    Tooltip, 
    Legend, 
    ResponsiveContainer 
} from 'recharts';

// Custom Smooth Scroll Helper (Slower than native scrollIntoView)
const smoothScroll = (target, duration) => {
    if (!target) return;
    const targetPosition = target.getBoundingClientRect().top + window.pageYOffset;
    const startPosition = window.pageYOffset;
    // Subtract a little offset (80px) for the sticky header
    const distance = targetPosition - startPosition - 80; 
    let startTime = null;

    const animation = (currentTime) => {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        
        // Easing function: easeInOutQuad for smooth acceleration/deceleration
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
    const [error, setError] = useState('');
    const [programs, setPrograms] = useState([]);
    const [careers, setCareers] = useState([]);
    const [selectedProgram, setSelectedProgram] = useState(null);
    const [selectedCareer, setSelectedCareer] = useState(null);
    const [isProgramOpen, setIsProgramOpen] = useState(false);
    const [isCareerOpen, setIsCareerOpen] = useState(false);
    const [optionsLoading, setOptionsLoading] = useState(true);
    const [optionsError, setOptionsError] = useState('');

    // Ref for scroll target
    const summaryRef = useRef(null);

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
        setError('');
        setShowResults(false);
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

            // Trigger custom smooth scroll with 2000ms duration (2 seconds)
            setTimeout(() => {
                smoothScroll(summaryRef.current, 2000);
            }, 100);

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    // --- CHART DATA ---
    const pieData = results ? [
        { name: 'Relevant Skills', value: results.matchingSkills, color: '#10b981' }, 
        { name: 'Other Topics', value: results.irrelevantSkills || 0, color: '#E5E7EB' } 
    ] : [];

    const barData = results ? [
        {
            name: 'Skill Analysis',
            Matches: results.matchingSkills,
            Gaps: results.missingSkills,
            Total: results.matchingSkills + results.missingSkills
        }
    ] : [];

    return (
        <div className="min-h-screen bg-gray-50 font-sans text-gray-900">
            {/* Header */}
            <header className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-50">
                <div className="max-w-6xl mx-auto flex items-center gap-2">
                    <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center shadow-sm">
                        <Layers className="w-5 h-5 text-white" />
                    </div>
                    <h1 className="text-xl font-bold text-gray-900 tracking-tight">TechGap</h1>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-6xl mx-auto px-6 py-12">
                
                {/* Title Section */}
                <div className="text-center mb-12 mt-4">
                    <h2 className="text-4xl md:text-5xl font-extrabold text-indigo-900 mb-4 tracking-tight">
                        Curriculum Gap Analyzer
                    </h2>
                    <p className="text-gray-600 text-lg mb-2 max-w-2xl mx-auto">
                        Identify critical skill gaps by comparing your course content against real-time industry job market standards.
                    </p>
                </div>

                {/* Control Panel */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 md:p-8 mb-12 transition-all hover:shadow-md">
                    <div className="flex flex-col md:flex-row items-end gap-4">
                        {/* Program Dropdown */}
                        <div className="w-full md:flex-1 relative">
                            <label className="block text-sm font-semibold text-gray-500 uppercase mb-2">Select Curriculum</label>
                            <button
                                onClick={() => {
                                    if (optionsLoading) return;
                                    setIsProgramOpen(!isProgramOpen);
                                    setIsCareerOpen(false);
                                }}
                                className="w-full flex items-center justify-between px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg hover:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-left disabled:opacity-60"
                                disabled={optionsLoading || programs.length === 0}
                            >
                                <div className="flex items-center gap-3 overflow-hidden">
                                    <BookOpen className="w-5 h-5 text-indigo-500 flex-shrink-0" />
                                    <span className="text-slate-700 font-medium truncate">
                                        {selectedProgram ? selectedProgram.label : optionsLoading ? 'Loading...' : 'No curriculum found'}
                                    </span>
                                </div>
                                <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${isProgramOpen ? 'rotate-180' : ''}`} />
                            </button>
                            {isProgramOpen && (
                                <div className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-xl py-1 max-h-60 overflow-auto">
                                    {programs.map((program) => (
                                        <button
                                            key={program.id}
                                            onClick={() => {
                                                setSelectedProgram(program);
                                                setIsProgramOpen(false);
                                                setShowResults(false);
                                            }}
                                            className="w-full text-left px-4 py-3 hover:bg-indigo-50 transition-colors flex items-center gap-2"
                                        >
                                            <span className={`block truncate ${selectedProgram?.id === program.id ? 'text-indigo-600 font-medium' : 'text-gray-700'}`}>
                                                {program.label}
                                            </span>
                                            {selectedProgram?.id === program.id && <CheckCircle className="w-4 h-4 text-indigo-600 ml-auto" />}
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Career Dropdown */}
                        <div className="w-full md:flex-1 relative">
                            <label className="block text-sm font-semibold text-gray-500 uppercase mb-2">Target Career Path</label>
                            <button
                                onClick={() => {
                                    if (optionsLoading) return;
                                    setIsCareerOpen(!isCareerOpen);
                                    setIsProgramOpen(false);
                                }}
                                className="w-full flex items-center justify-between px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg hover:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-left disabled:opacity-60"
                                disabled={optionsLoading || careers.length === 0}
                            >
                                <div className="flex items-center gap-3 overflow-hidden">
                                    <BarChart3 className="w-5 h-5 text-indigo-500 flex-shrink-0" />
                                    <span className="text-slate-700 font-medium truncate">
                                        {selectedCareer ? selectedCareer.label : optionsLoading ? 'Loading...' : 'No job roles found'}
                                    </span>
                                </div>
                                <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${isCareerOpen ? 'rotate-180' : ''}`} />
                            </button>
                            {isCareerOpen && (
                                <div className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-xl py-1 max-h-80 overflow-y-auto">
                                    {careers.map((career) => (
                                        <button
                                            key={career.id}
                                            onClick={() => {
                                                setSelectedCareer(career);
                                                setIsCareerOpen(false);
                                                setShowResults(false);
                                            }}
                                            className="w-full text-left px-4 py-3 hover:bg-indigo-50 transition-colors flex items-center gap-2"
                                        >
                                            <span className={`block truncate ${selectedCareer?.id === career.id ? 'text-indigo-600 font-medium' : 'text-gray-700'}`}>
                                                {career.label}
                                            </span>
                                            {selectedCareer?.id === career.id && <CheckCircle className="w-4 h-4 text-indigo-600 ml-auto" />}
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Analyze Button */}
                        <div className="w-full md:w-auto">
                            <button 
                                onClick={handleAnalyze}
                                className="w-full md:w-auto px-8 py-3 bg-indigo-600 text-white rounded-lg font-bold shadow-lg hover:bg-indigo-700 hover:shadow-indigo-500/30 transform active:scale-95 transition-all flex items-center justify-center h-[48px]"
                                disabled={loading || !selectedProgram || !selectedCareer}
                            >
                                {loading ? 'Analyzing...' : 'Run Analysis'}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Scroll Anchor */}
                <div ref={summaryRef}></div>

                {/* Results Section */}
                {optionsError && <div className="text-red-500 mb-4 bg-red-50 p-4 rounded-lg border border-red-200">{optionsError}</div>}
                {error && <div className="text-red-500 mb-4 bg-red-50 p-4 rounded-lg border border-red-200">{error}</div>}
                
                {showResults && results && (
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 pb-10">
                        
                        {/* 1. Summary Metrics Cards */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                            <StatCard 
                                label="Total Required Skills" 
                                value={results.matchingSkills + results.missingSkills} 
                                icon={<Target className="w-5 h-5 text-slate-600" />}
                            />
                            <StatCard 
                                label="Matches Found" 
                                value={results.matchingSkills} 
                                color="text-emerald-600"
                                icon={<CheckCircle className="w-5 h-5 text-emerald-600" />}
                            />
                            <StatCard 
                                label="Critical Gaps" 
                                value={results.missingSkills} 
                                color="text-red-500"
                                icon={<AlertCircle className="w-5 h-5 text-red-500" />}
                            />
                            {/* CHANGED: Now displays Job Coverage, icon changed to BarChart3 to use existing imports */}
                            <StatCard 
                                label="Job Coverage" 
                                value={results.coverage} 
                                subtext="of job requirements met"
                                color="text-indigo-600"
                                icon={<BarChart3 className="w-5 h-5 text-indigo-600" />}
                            />
                        </div>

                        {/* 2. Visualizations Section (Charts) */}
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                            
                            {/* Chart A: Curriculum Relevance */}
                            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow duration-300">
                                <h4 className="text-lg font-bold text-slate-800 mb-4">Curriculum Relevance</h4>
                                <div className="h-64 w-full relative">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <PieChart>
                                            <Pie
                                                data={pieData}
                                                cx="50%"
                                                cy="50%"
                                                innerRadius="60%"
                                                outerRadius="80%"
                                                paddingAngle={5}
                                                dataKey="value"
                                                stroke="none"
                                            >
                                                {pieData.map((entry, index) => (
                                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                                ))}
                                            </Pie>
                                            {/* Tooltip component has been removed */}
                                            <Legend verticalAlign="bottom" height={36} iconType="circle" />
                                        </PieChart>
                                    </ResponsiveContainer>
                                    
                                    {/* Center Text Overlay */}
                                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                                        <div className="text-center pb-8"> 
                                            <p className="text-3xl font-bold text-slate-800">{results.relevance}</p>
                                            <p className="text-xs text-slate-400">Relevant</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Chart B: Gap Analysis Bars */}
                            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow duration-300">
                                <h4 className="text-lg font-bold text-slate-800 mb-4">Gap Analysis Overview</h4>
                                <div className="h-64 w-full">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart data={barData} layout="horizontal" barSize={40}>
                                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                            <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#94a3b8'}} />
                                            <YAxis axisLine={false} tickLine={false} tick={{fill: '#94a3b8'}} />
                                            <Tooltip 
                                                cursor={{fill: '#f8fafc'}}
                                                contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                            />
                                            <Legend iconType="circle" />
                                            <Bar dataKey="Matches" name="Matches" fill="#10b981" radius={[4, 4, 0, 0]} />
                                            <Bar dataKey="Gaps" name="Missing Gaps" fill="#ef4444" radius={[4, 4, 0, 0]} />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        </div>

                        {/* 3. Detailed Comparison Lists */}
                        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden hover:shadow-md transition-shadow duration-300">
                            <div className="bg-slate-50/50 px-6 py-4 border-b border-slate-100">
                                <h4 className="font-bold text-slate-800">Skill Details</h4>
                            </div>
                            <div className="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-100">
                                {/* Exact Matches */}
                                <div className="p-6">
                                    <div className="flex items-center gap-2 mb-4">
                                        <CheckCircle className="w-5 h-5 text-emerald-500" />
                                        <h5 className="font-semibold text-slate-700">Matched Skills (Covered)</h5>
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                        {results.exact && results.exact.length > 0 ? (
                                            results.exact.map((skill, index) => (
                                                <span key={index} className="px-3 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full text-sm font-medium">
                                                    {skill}
                                                </span>
                                            ))
                                        ) : (
                                            <span className="text-slate-400 text-sm italic">No exact matches.</span>
                                        )}
                                    </div>
                                </div>

                                {/* Missing Skills */}
                                <div className="p-6 bg-red-50/5">
                                    <div className="flex items-center gap-2 mb-4">
                                        <AlertCircle className="w-5 h-5 text-red-500" />
                                        <h5 className="font-semibold text-slate-700">Missing Skills (Gaps)</h5>
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                        {results.gaps && results.gaps.length > 0 ? (
                                            results.gaps.map((skill, index) => (
                                                <span key={index} className="px-3 py-1 bg-red-50 text-red-700 border border-red-200 rounded-full text-sm font-medium">
                                                    {skill}
                                                </span>
                                            ))
                                        ) : (
                                            <span className="text-slate-400 text-sm italic">No missing skills found.</span>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}

// Reusable Card Component with Hover Effects
const StatCard = ({ label, value, color = "text-slate-800", subtext, icon }) => (
  <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 cursor-default">
    <div className="flex items-center justify-between mb-4">
      <div className={`p-2 rounded-lg bg-slate-50 ${color.replace('text-', 'bg-').replace('600', '100').replace('500', '100')}`}>
        {icon}
      </div>
    </div>
    <h4 className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-1">{label}</h4>
    <div className={`text-3xl font-extrabold ${color}`}>
      {value}
    </div>
    {subtext && <p className="text-xs text-slate-400 mt-2">{subtext}</p>}
  </div>
);