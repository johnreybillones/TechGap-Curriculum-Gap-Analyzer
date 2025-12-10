/**
 * ChartsSection Component
 * Container for both charts
 */
import RelevancePieChart from './RelevancePieChart';
import GapBarChart from './GapBarChart';

const ChartsSection = ({ results, darkMode }) => {
    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6 mb-6 md:mb-8">
            <RelevancePieChart results={results} />
            <GapBarChart results={results} darkMode={darkMode} />
        </div>
    );
};

export default ChartsSection;
