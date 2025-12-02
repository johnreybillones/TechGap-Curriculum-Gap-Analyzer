import React, { useState } from 'react';
import { FileText, ChevronDown, BarChart3, CheckCircle, AlertCircle, BookOpen } from 'lucide-react';

// Mock data derived from your ml_model/results.csv
// In a real scenario, this would come from your backend API
const RESULTS_DATA = {
  'DLSU-D CS-Intelligent Systems': {
    cluster: 'Cluster_1',
    confidence: '98.7%',
    alignment: '99.9%',
    coverage: '100.0%',
    matchingSkills: 46,
    missingSkills: 334,
    covered: ['lan', 'sql', 'machine learning', 'java', 'python'],
    gaps: ['aws', 'business intelligence', 'data warehouse', 'excel', 'full stack', 'git', 'information security', 'linux', 'scala', 'ssis']
  },
  'DLSU-D CS-Game Development': {
    cluster: 'Cluster_0',
    confidence: '61.4%',
    alignment: '99.8%',
    coverage: '100.0%',
    matchingSkills: 31,
    missingSkills: 349,
    covered: ['lan', 'sql', 'git', 'java', 'python'],
    gaps: ['artificial intelligence', 'aws', 'business intelligence', 'data analysis', 'data analytics', 'data warehouse', 'excel', 'full stack', 'information security', 'less', 'linux', 'machine learning', 'scala', 'ssis']
  },
  'DLSU-D IT-Networking': { // Mapped from IT Network Technology
    cluster: 'Cluster_0',
    confidence: '59.2%',
    alignment: '99.9%',
    coverage: '98.2%',
    matchingSkills: 56,
    missingSkills: 324,
    covered: ['lan', 'machine learning', 'git', 'java', 'python'],
    gaps: ['aws', 'business intelligence', 'data analysis', 'data warehouse', 'excel', 'full stack', 'information security', 'scala', 'sql', 'ssis']
  },
  'DLSU-D IT-Web Development': {
    cluster: 'Cluster_2',
    confidence: '63.1%',
    alignment: '99.8%',
    coverage: '97.7%',
    matchingSkills: 42,
    missingSkills: 338,
    covered: ['lan', 'sql', 'java', 'python'],
    gaps: ['artificial intelligence', 'aws', 'business intelligence', 'data analysis', 'data analytics', 'data warehouse', 'excel', 'full stack', 'git', 'information security', 'machine learning', 'scala', 'ssis']
  }
};

export default function CurriculumGapAnalyzer() {
  const [selectedProgram, setSelectedProgram] = useState('DLSU-D CS-Intelligent Systems');
  const [selectedCareer, setSelectedCareer] = useState('Data Scientist');
  const [isProgramOpen, setIsProgramOpen] = useState(false);
  const [isCareerOpen, setIsCareerOpen] = useState(false);
  const [showResults, setShowResults] = useState(false);

  const programs = [
    'DLSU-D CS-Intelligent Systems',
    'DLSU-D CS-Game Development',
    'DLSU-D IT-Web Development',
    'DLSU-D IT-Networking'
  ];

  const careerOpportunities = [
    'Data Scientist',
    'Data Analyst',
    'Data Architect',
    'Data Engineer',
    'Statistics',
    'Database Administrator',
    'Business Analyst',
    'Data and Analytics Manager',
    'Machine Learning',
    'Artificial Intelligence',
    'Deep Learning',
    'Business Intelligence Analyst',
    'Data Visualization Expert',
    'Data Quality Manager',
    'Big Data Engineer',
    'Data Warehousing',
    'Technology Integration',
    'IT Consultant',
    'IT Systems Administrator',
    'Cloud Architect',
    'Technical Operations',
    'Cloud Services Developer',
    'Full Stack Developer',
    'Information Security Analyst',
    'Network Architect'
  ];

  const handleAnalyze = () => {
    setShowResults(true);
  };

  const currentResult = RESULTS_DATA[selectedProgram];

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
                  setIsProgramOpen(!isProgramOpen);
                  setIsCareerOpen(false);
                }}
                className="w-full flex items-center justify-between px-4 py-3 bg-white border border-gray-300 rounded-lg hover:border-indigo-500 hover:ring-1 hover:ring-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-left"
              >
                <div className="flex items-center gap-3 overflow-hidden">
                  <BookOpen className="w-5 h-5 text-indigo-600 flex-shrink-0" />
                  <span className="text-gray-900 truncate">{selectedProgram}</span>
                </div>
                <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${isProgramOpen ? 'rotate-180' : ''}`} />
              </button>
              
              {isProgramOpen && (
                <div className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-xl py-1 max-h-60 overflow-auto">
                  {programs.map((program) => (
                    <button
                      key={program}
                      onClick={() => {
                        setSelectedProgram(program);
                        setIsProgramOpen(false);
                        setShowResults(false); // Reset results on change
                      }}
                      className="w-full text-left px-4 py-3 hover:bg-indigo-50 transition-colors flex items-center gap-2"
                    >
                      <span className={`block truncate ${selectedProgram === program ? 'text-indigo-600 font-medium' : 'text-gray-700'}`}>
                        {program}
                      </span>
                      {selectedProgram === program && <CheckCircle className="w-4 h-4 text-indigo-600 ml-auto" />}
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
                  setIsCareerOpen(!isCareerOpen);
                  setIsProgramOpen(false);
                }}
                className="w-full flex items-center justify-between px-4 py-3 bg-white border border-gray-300 rounded-lg hover:border-indigo-500 hover:ring-1 hover:ring-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-left"
              >
                <div className="flex items-center gap-3 overflow-hidden">
                  <BarChart3 className="w-5 h-5 text-indigo-600 flex-shrink-0" />
                  <span className="text-gray-900 truncate">{selectedCareer}</span>
                </div>
                <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${isCareerOpen ? 'rotate-180' : ''}`} />
              </button>
              
              {isCareerOpen && (
                <div className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-xl py-1 max-h-80 overflow-y-auto">
                  {careerOpportunities.map((career) => (
                    <button
                      key={career}
                      onClick={() => {
                        setSelectedCareer(career);
                        setIsCareerOpen(false);
                        setShowResults(false);
                      }}
                      className="w-full text-left px-4 py-3 hover:bg-indigo-50 transition-colors flex items-center gap-2"
                    >
                       <span className={`block truncate ${selectedCareer === career ? 'text-indigo-600 font-medium' : 'text-gray-700'}`}>
                        {career}
                      </span>
                      {selectedCareer === career && <CheckCircle className="w-4 h-4 text-indigo-600 ml-auto" />}
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
              >
                Run Analysis
              </button>
            </div>
          </div>
        </div>

        {/* Results Section */}
        {showResults && currentResult && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center gap-2 mb-6">
              <div className="h-8 w-1 bg-indigo-600 rounded-full"></div>
              <h3 className="text-2xl font-bold text-gray-900">Analysis Results</h3>
            </div>

            {/* High Level Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                <p className="text-sm text-gray-500 font-medium mb-1">Curriculum Coverage</p>
                <p className="text-3xl font-bold text-indigo-600">{currentResult.coverage}</p>
              </div>
              <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                <p className="text-sm text-gray-500 font-medium mb-1">Semantic Alignment</p>
                <p className="text-3xl font-bold text-indigo-600">{currentResult.alignment}</p>
              </div>
              <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                <p className="text-sm text-gray-500 font-medium mb-1">Matching Skills</p>
                <p className="text-3xl font-bold text-emerald-600">{currentResult.matchingSkills}</p>
              </div>
               <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                <p className="text-sm text-gray-500 font-medium mb-1">Missing Skills</p>
                <p className="text-3xl font-bold text-red-500">{currentResult.missingSkills}</p>
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
                    {currentResult.covered.map((skill, index) => (
                      <span key={index} className="px-3 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full text-sm font-medium">
                        {skill}
                      </span>
                    ))}
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
                    {currentResult.gaps.map((skill, index) => (
                      <span key={index} className="px-3 py-1 bg-red-50 text-red-700 border border-red-200 rounded-full text-sm font-medium">
                        {skill}
                      </span>
                    ))}
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