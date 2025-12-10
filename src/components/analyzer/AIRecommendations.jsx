/**
 * AIRecommendations Component
 * Collapsible AI recommendations section
 */
import { ChevronDown, Sparkles, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const AIRecommendations = ({ isOpen, setIsOpen, loading, recommendation }) => {
    return (
        <div className="bg-white/80 dark:bg-slate-800/50 backdrop-blur-md rounded-2xl shadow-sm border border-indigo-50 dark:border-slate-700/50 mb-6 md:mb-8 relative overflow-hidden transition-all duration-300 hover:shadow-md hover:border-indigo-200 dark:hover:border-indigo-900/50 group">
            <div 
                className="flex items-center justify-between p-4 md:p-6 cursor-pointer select-none hover:bg-indigo-50/30 dark:hover:bg-indigo-900/10 transition-colors duration-300"
                onClick={() => setIsOpen(!isOpen)}
            >
                <div className="flex items-center gap-3 relative z-10">
                    <div className="p-2 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-lg shadow-lg shadow-indigo-500/20 group-hover:scale-110 transition-transform duration-300">
                        <Sparkles className="w-4 h-4 text-white" />
                    </div>
                    <h3 className="text-sm md:text-xl font-bold text-indigo-900 dark:text-slate-200">AI Recommendations</h3>
                </div>
                <div className={`text-indigo-400 transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`}>
                    <ChevronDown className="w-5 h-5"/>
                </div>
            </div>
            
            <div className={`grid transition-all duration-300 ease-in-out ${isOpen ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'}`}>
                <div className="overflow-hidden">
                    <div className="px-4 pb-4 md:px-6 md:pb-6">
                        {loading ? (
                            <div className="flex items-center gap-3 text-indigo-600 dark:text-indigo-400 py-6 animate-pulse bg-indigo-50/50 dark:bg-indigo-900/10 rounded-xl p-4">
                                <Loader2 className="w-5 h-5 animate-spin" />
                                <span className="text-sm font-medium">Analyzing curriculum gaps...</span>
                            </div>
                        ) : recommendation ? (
                            <div className="prose prose-sm md:prose-base prose-indigo max-w-none text-slate-700 dark:text-slate-300 bg-indigo-50/30 dark:bg-indigo-900/10 p-5 rounded-xl border border-indigo-50 dark:border-slate-700/50 shadow-inner dark:shadow-none">
                                <ReactMarkdown components={{
                                    ul: (props) => <ul className="list-disc pl-5 space-y-2 mt-3" {...props} />,
                                    ol: (props) => <ol className="list-decimal pl-5 space-y-2 mt-3" {...props} />,
                                    li: (props) => <li className="text-slate-700 dark:text-slate-300" {...props} />,
                                    p: (props) => <p className="text-slate-700 dark:text-slate-300 leading-relaxed mb-4" {...props} />,
                                    h1: (props) => <h1 className="text-lg md:text-xl font-bold text-indigo-800 dark:text-indigo-200 mb-2 mt-5" {...props} />,
                                    h2: (props) => <h2 className="text-base md:text-lg font-bold text-indigo-900 dark:text-indigo-200 mb-2 mt-5" {...props} />,
                                    h3: (props) => <h3 className="text-base font-semibold text-indigo-900 dark:text-indigo-200 mb-2 mt-4" {...props} />,
                                    strong: (props) => <strong className="text-indigo-900 dark:text-indigo-300 font-bold" {...props} />,
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
    );
};

export default AIRecommendations;
