import React, { useEffect, useState } from 'react';
import { FileText, ChevronDown, BarChart3, CheckCircle, AlertCircle, BookOpen } from 'lucide-react';

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

    useEffect(() => {
        const loadOptions = async () => {
            try {
                setOptionsError('');
                setOptionsLoading(true);
                // Prefer curated options from backend; fallback to raw lists
                const optionsRes = await fetch(`${API_BASE}/api/options`);
                const optionsCt = optionsRes.headers.get('content-type') || '';
                let mappedCurr = [];
                let mappedJobs = [];

                const toJson = async (res) => {
                    const ct = res.headers.get('content-type') || '';
                    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
                    if (!ct.includes('application/json')) throw new Error('Unexpected response (not JSON)');
                    return res.json();
                };

                if (optionsRes.ok && optionsCt.includes('application/json')) {
                    const opts = await optionsRes.json();
                    mappedCurr = (opts.curricula || []).filter((c) => c.id && c.label);
                    mappedJobs = (opts.jobs || []).filter((j) => j.id && j.label);
                } else {
                    const [currRes, jobRes] = await Promise.all([
                        fetch(`${API_BASE}/curriculum/`),
                        fetch(`${API_BASE}/job-role/`),
                    ]);
                    const [currData, jobData] = await Promise.all([
                        toJson(currRes),
                        toJson(jobRes),
                    ]);
                    mappedCurr = (currData || [])
                        .map((c) => ({
                            id: c.curriculum_id,
                            label: c.track || c.course_title || `Curriculum ${c.curriculum_id}`,
                        }))
                        .filter((c) => !!c.label);
                    mappedJobs = (jobData || [])
                        .map((j) => ({
                            id: j.job_id,
                            label: j.query || j.title || `Job ${j.job_id}`,
                        }))
                        .filter((j) => !!j.label);
                }

                setPrograms(mappedCurr);
                setCareers(mappedJobs);
                if (mappedCurr.length > 0) {
                    setSelectedProgram(mappedCurr[0]);
                }
                if (mappedJobs.length > 0) {
                    setSelectedCareer(mappedJobs[0]);
                }
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
            const ct = response.headers.get('content-type') || '';
            if (!response.ok) {
                throw new Error(`Failed to fetch analysis (${response.status})`);
            }
            if (!ct.includes('application/json')) {
                throw new Error('Unexpected response (not JSON)');
            }
            const data = await response.json();
            setResults(data);
            setShowResults(true);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 font-sans">
            {/* Header */}
            <header className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-50">
                <div className="max-w-6xl mx-auto flex items-center gap-2">
                    <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center shadow-sm">
                        <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M12 2L2 7l10 5 10-5-10-5z" />
                            <path d="M2 17l10 5 10-5" />
                            <path d="M2 12l10 5 10-5" />
                        </svg>
                    </div>
                    <h1 className="text-xl font-bold text-gray-900 tracking-tight">Curriculum Gap Analyzer</h1>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-6xl mx-auto px-6 py-12">
                {/* AI Badge */}
                <div className="flex justify-center mb-6">
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-50 border border-indigo-100 rounded-full shadow-sm">
                        <svg className="w-4 h-4 text-indigo-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <circle cx="12" cy="12" r="10" />
                            <path d="M12 6v6l4 2" />
                        </svg>
                        <span className="text-sm font-medium text-indigo-700">AI-powered insights for universities</span>
                    </div>
                </div>

                {/* Title Section */}
                <div className="text-center mb-12">
                    <h2 className="text-4xl md:text-5xl font-extrabold text-indigo-900 mb-4 tracking-tight">
                        Analyze Your Curriculum
                    </h2>
                    <p className="text-gray-600 text-lg mb-2 max-w-2xl mx-auto">
                        Identify critical skill gaps by comparing your course content against real-time industry job market standards.
                    </p>
                </div>

                {/* Control Panel */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 md:p-8 mb-8 transition-all hover:shadow-md">
                    <div className="flex flex-col md:flex-row items-center gap-4">
                        {/* Program Dropdown */}
                        <div className="w-full md:flex-1 relative">
                            <label className="block text-sm font-semibold text-gray-700 mb-2">Select Curriculum</label>
                            <button
                                onClick={() => {
                                    if (optionsLoading) return;
                                    setIsProgramOpen(!isProgramOpen);
                                    setIsCareerOpen(false);
                                }}
                                className="w-full flex items-center justify-between px-4 py-3 bg-white border border-gray-300 rounded-lg hover:border-indigo-500 hover:ring-1 hover:ring-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-left disabled:opacity-60"
                                disabled={optionsLoading || programs.length === 0}
                            >
                                <div className="flex items-center gap-3 overflow-hidden">
                                    <BookOpen className="w-5 h-5 text-indigo-600 flex-shrink-0" />
                                    <span className="text-gray-900 truncate">
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
                            <label className="block text-sm font-semibold text-gray-700 mb-2">Target Career Path</label>
                            <button
                                onClick={() => {
                                    if (optionsLoading) return;
                                    setIsCareerOpen(!isCareerOpen);
                                    setIsProgramOpen(false);
                                }}
                                className="w-full flex items-center justify-between px-4 py-3 bg-white border border-gray-300 rounded-lg hover:border-indigo-500 hover:ring-1 hover:ring-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-left disabled:opacity-60"
                                disabled={optionsLoading || careers.length === 0}
                            >
                                <div className="flex items-center gap-3 overflow-hidden">
                                    <BarChart3 className="w-5 h-5 text-indigo-600 flex-shrink-0" />
                                    <span className="text-gray-900 truncate">
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
                        <div className="w-full md:w-auto mt-7">
                            <button 
                                onClick={handleAnalyze}
                                className="w-full md:w-auto px-8 py-3.5 bg-indigo-600 text-white rounded-lg font-semibold shadow-md hover:bg-indigo-700 hover:shadow-lg transform active:scale-95 transition-all"
                                disabled={loading || !selectedProgram || !selectedCareer}
                            >
                                {loading ? 'Analyzing...' : 'Run Analysis'}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Results Section */}
                {optionsError && <div className="text-red-500 mb-4">{optionsError}</div>}
                {error && <div className="text-red-500 mb-4">{error}</div>}
                {showResults && results && (
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 max-h-[70vh] overflow-y-auto pr-2">
                        <div className="flex items-center gap-2 mb-6">
                            <div className="h-8 w-1 bg-indigo-600 rounded-full"></div>
                            <h3 className="text-2xl font-bold text-gray-900">Analysis Results</h3>
                        </div>

                        {/* High Level Metrics */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                            <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                                <p className="text-sm text-gray-500 font-medium mb-1">Curriculum Coverage</p>
                                <p className="text-3xl font-bold text-indigo-600">{results.coverage}</p>
                            </div>
                            <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                                <p className="text-sm text-gray-500 font-medium mb-1">Semantic Alignment</p>
                                <p className="text-3xl font-bold text-indigo-600">{results.alignment}</p>
                            </div>
                            <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                                <p className="text-sm text-gray-500 font-medium mb-1">Matching Skills</p>
                                <p className="text-3xl font-bold text-emerald-600">{results.matchingSkills}</p>
                            </div>
                            <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                                <p className="text-sm text-gray-500 font-medium mb-1">Missing Skills</p>
                                <p className="text-3xl font-bold text-red-500">{results.missingSkills}</p>
                            </div>
                        </div>

                        {/* Detailed Comparison Table */}
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                            <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
                                <h4 className="font-semibold text-gray-900">Skill Gap Analysis</h4>
                            </div>
                            <div className="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-gray-200">
                                {/* Covered Skills */}
                                <div className="p-6">
                                    <div className="flex items-center gap-2 mb-4">
                                        <CheckCircle className="w-5 h-5 text-emerald-500" />
                                        <h5 className="font-semibold text-gray-900">Top Skills Covered</h5>
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                        {results.covered && results.covered.length > 0 ? (
                                            results.covered.map((skill, index) => (
                                                <span key={index} className="px-3 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full text-sm font-medium">
                                                    {skill}
                                                </span>
                                            ))
                                        ) : (
                                            <span className="text-gray-400">No covered skills found.</span>
                                        )}
                                    </div>
                                    <p className="mt-4 text-sm text-gray-500">
                                        These skills are present in your curriculum and highly relevant to the target career.
                                    </p>
                                </div>

                                {/* Missing Skills */}
                                <div className="p-6 bg-red-50/10">
                                    <div className="flex items-center gap-2 mb-4">
                                        <AlertCircle className="w-5 h-5 text-red-500" />
                                        <h5 className="font-semibold text-gray-900">Critical Skill Gaps</h5>
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                        {results.gaps && results.gaps.length > 0 ? (
                                            results.gaps.map((skill, index) => (
                                                <span key={index} className="px-3 py-1 bg-red-50 text-red-700 border border-red-200 rounded-full text-sm font-medium">
                                                    {skill}
                                                </span>
                                            ))
                                        ) : (
                                            <span className="text-gray-400">No missing skills found.</span>
                                        )}
                                    </div>
                                    <p className="mt-4 text-sm text-gray-500">
                                        These are high-demand skills found in job postings that are currently missing from the curriculum.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
