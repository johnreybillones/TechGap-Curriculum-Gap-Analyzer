/**
 * Dropdown Component
 * Reusable dropdown selector
 */
import { ChevronDown, CheckCircle } from 'lucide-react';

const Dropdown = ({ 
    label, 
    icon: Icon, 
    options, 
    selected, 
    onSelect, 
    isOpen, 
    onToggle, 
    onClose,
    loading = false,
    placeholder = "Select an option"
}) => {
    return (
        <div className="w-full md:flex-1 relative group">
            <label className="block text-xs md:text-sm font-bold text-slate-500 dark:text-slate-400 uppercase mb-2 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors ml-1">
                {label}
            </label>
            <button
                onClick={onToggle}
                className="w-full flex items-center justify-between px-4 py-4 bg-slate-50/80 dark:bg-slate-900/30 border border-slate-200 dark:border-slate-700/50 rounded-xl hover:border-indigo-500 dark:hover:border-indigo-500/50 hover:bg-white dark:hover:bg-slate-800/50 focus:outline-none focus:ring-4 focus:ring-indigo-100 dark:focus:ring-indigo-900/20 transition-all text-left disabled:opacity-60 shadow-sm hover:shadow-lg hover:scale-[1.01] hover:shadow-indigo-200/30 dark:hover:shadow-indigo-900/20 cursor-pointer"
                disabled={loading || options.length === 0}
            >
                <div className="flex items-center gap-3 overflow-hidden">
                    {Icon && <Icon className="w-5 h-5 text-indigo-500 dark:text-indigo-400 flex-shrink-0" />}
                    <span className="text-slate-700 dark:text-slate-200 font-bold truncate text-sm md:text-base">
                        {selected ? selected.label : loading ? 'Loading...' : placeholder}
                    </span>
                </div>
                <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform duration-300 ${isOpen ? 'rotate-180 text-indigo-500 dark:text-indigo-400' : ''}`} />
            </button>
            
            <div className={`absolute z-50 w-full mt-2 bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700/50 rounded-xl shadow-2xl overflow-hidden transition-all duration-200 origin-top ${isOpen ? 'opacity-100 scale-100 translate-y-0' : 'opacity-0 scale-95 -translate-y-2 pointer-events-none'}`}>
                <div className="max-h-64 overflow-auto py-1 scrollbar-thin scrollbar-thumb-indigo-100 dark:scrollbar-thumb-indigo-900 scrollbar-track-transparent">
                    {options.map((option) => (
                        <button
                            key={option.id}
                            onClick={() => {
                                onSelect(option);
                                onClose();
                            }}
                            className="w-full text-left px-4 py-3 hover:bg-indigo-50 dark:hover:bg-slate-700/30 transition-colors flex items-center gap-3 border-b border-slate-50 dark:border-slate-700/30 last:border-0"
                        >
                            <span className={`block truncate text-sm ${selected?.id === option.id ? 'text-indigo-600 dark:text-indigo-400 font-bold' : 'text-slate-600 dark:text-slate-300'}`}>
                                {option.label}
                            </span>
                            {selected?.id === option.id && <CheckCircle className="w-4 h-4 text-indigo-600 dark:text-indigo-400 ml-auto" />}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Dropdown;
