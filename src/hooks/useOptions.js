/**
 * useOptions Hook
 * Manages fetching and state for curriculum and career options
 */
import { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export const useOptions = () => {
    const [programs, setPrograms] = useState([]);
    const [careers, setCareers] = useState([]);
    const [selectedProgram, setSelectedProgram] = useState(null);
    const [selectedCareer, setSelectedCareer] = useState(null);
    const [isProgramOpen, setIsProgramOpen] = useState(false);
    const [isCareerOpen, setIsCareerOpen] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const loadOptions = async () => {
            try {
                setError('');
                setLoading(true);
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
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        loadOptions();
    }, []);

    return {
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
        loading,
        error
    };
};

export default useOptions;
