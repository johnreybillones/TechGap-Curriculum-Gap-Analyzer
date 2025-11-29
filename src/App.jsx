import React, { useState } from 'react';
import { FileText, ChevronDown } from 'lucide-react';

export default function CurriculumGapAnalyzer() {
  const [selectedProgram, setSelectedProgram] = useState('DLSU-D CS-Intelligent Systems');
  const [selectedCareer, setSelectedCareer] = useState('Software Engineer / Developer');
  const [isProgramOpen, setIsProgramOpen] = useState(false);
  const [isCareerOpen, setIsCareerOpen] = useState(false);

  const programs = [
    'DLSU-D CS-Intelligent Systems',
    'DLSU-D CS-Game Development',
    'DLSU-D IT-Web Development',
    'DLSU-D IT-Networking'
  ];

  const careerOpportunities = [
    'Software Engineer / Developer',
    'Web Developer (Front-End, Back-End, Full-Stack)',
    'Mobile App Developer',
    'Game Developer',
    'Data Scientist',
    'Machine Learning Engineer',
    'Cybersecurity Analyst',
    'Ethical Hacker / Penetration Tester',
    'Security Engineer',
    'Systems Administrator',
    'Network Administrator',
    'Cloud Engineer',
    'DevOps Engineer',
    'Database Administrator (DBA)',
    'Database Developer'
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
            <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <h1 className="text-xl font-semibold text-gray-900">Curriculum Gap Analyzer</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-12">
        {/* AI Badge */}
        <div className="flex justify-center mb-6">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-50 rounded-full">
            <svg className="w-4 h-4 text-indigo-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 6v6l4 2" />
            </svg>
            <span className="text-sm text-indigo-700">AI-powered insights for universities</span>
          </div>
        </div>

        {/* Title Section */}
        <div className="text-center mb-12">
          <h2 className="text-5xl font-bold text-indigo-900 mb-4">
            Curriculum Gap Analyzer
          </h2>
          <p className="text-gray-600 text-lg mb-2">
            Analyze course curricula against current job market standards and emerging technologies.
          </p>
          <p className="text-gray-600 text-lg">
            Choose a dataset and a standard to see gaps and recommendations.
          </p>
        </div>

        {/* Dropdowns Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8">
          <div className="flex items-center gap-4 mb-6">
            {/* Program Dropdown */}
            <div className="flex-1 relative">
              <button
                onClick={() => {
                  setIsProgramOpen(!isProgramOpen);
                  setIsCareerOpen(false);
                }}
                className="w-full flex items-center justify-between px-4 py-3 bg-white border border-gray-300 rounded-lg hover:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              >
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-indigo-600" />
                  <span className="text-gray-900">{selectedProgram}</span>
                </div>
                <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${isProgramOpen ? 'rotate-180' : ''}`} />
              </button>
              
              {isProgramOpen && (
                <div className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg">
                  {programs.map((program) => (
                    <button
                      key={program}
                      onClick={() => {
                        setSelectedProgram(program);
                        setIsProgramOpen(false);
                      }}
                      className="w-full text-left px-4 py-3 hover:bg-indigo-50 first:rounded-t-lg last:rounded-b-lg transition-colors"
                    >
                      <span className={`${selectedProgram === program ? 'text-indigo-600 font-medium' : 'text-gray-900'}`}>
                        {program}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Career Dropdown */}
            <div className="flex-1 relative">
              <button
                onClick={() => {
                  setIsCareerOpen(!isCareerOpen);
                  setIsProgramOpen(false);
                }}
                className="w-full flex items-center justify-between px-4 py-3 bg-white border border-gray-300 rounded-lg hover:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              >
                <span className="text-gray-900">{selectedCareer}</span>
                <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${isCareerOpen ? 'rotate-180' : ''}`} />
              </button>
              
              {isCareerOpen && (
                <div className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg max-h-80 overflow-y-auto">
                  {careerOpportunities.map((career) => (
                    <button
                      key={career}
                      onClick={() => {
                        setSelectedCareer(career);
                        setIsCareerOpen(false);
                      }}
                      className="w-full text-left px-4 py-3 hover:bg-indigo-50 first:rounded-t-lg last:rounded-b-lg transition-colors"
                    >
                      <span className={`${selectedCareer === career ? 'text-indigo-600 font-medium' : 'text-gray-900'}`}>
                        {career}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Analyze Button */}
            <button className="px-8 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors">
              Analyze
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}