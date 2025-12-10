/**
 * Header Component
 * App header with logo and dark mode toggle
 */
import { Sun, Moon } from 'lucide-react';
import { TechGapLogo } from '../common';

const Header = ({ darkMode, setDarkMode }) => {
    return (
        <header className="bg-white/70 dark:bg-slate-900/50 backdrop-blur-xl border-b border-slate-100 dark:border-slate-800/30 px-4 md:px-6 py-3 sticky top-0 z-40 shadow-sm transition-all duration-300">
            <div className="max-w-6xl mx-auto flex items-center gap-2">
                <div className="w-8 h-8 flex items-center justify-center transform hover:scale-105 transition-transform duration-300">
                    <TechGapLogo className="w-8 h-8 drop-shadow-md" />
                </div>
                <h1 className="text-lg md:text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-700 to-indigo-600 dark:from-slate-200 dark:to-indigo-300 tracking-tight">
                    TechGap
                </h1>
                
                {/* Dark Mode Toggle */}
                <button 
                    onClick={() => setDarkMode(!darkMode)}
                    className={`ml-auto relative w-16 h-8 rounded-full transition-all duration-500 focus:outline-none shadow-inner border border-slate-200 dark:border-slate-700 cursor-pointer z-50 hover:scale-110 hover:shadow-lg ${darkMode ? 'bg-slate-800 hover:bg-slate-700' : 'bg-indigo-50 hover:bg-indigo-100'}`}
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
    );
};

export default Header;
