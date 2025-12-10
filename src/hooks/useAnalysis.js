/**
 * useAnalysis Hook
 * Manages the gap analysis state and API calls
 */
import { useState, useRef } from 'react';
import { smoothScroll } from '../utils/scroll';

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export const useAnalysis = () => {
    const [showResults, setShowResults] = useState(false);
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    
    // AI Recommendation State
    const [recommendation, setRecommendation] = useState('');
    const [recLoading, setRecLoading] = useState(false);
    const [isAiOpen, setIsAiOpen] = useState(true);

    // Skill List State
    const [showAllGaps, setShowAllGaps] = useState(false);
    const [showAllMatches, setShowAllMatches] = useState(false);

    // Refs
    const summaryRef = useRef(null);
    const matchedSkillsRef = useRef(null);
    const missingSkillsRef = useRef(null);

    // Toggle handlers with scroll behavior
    const handleToggleMatches = () => {
        if (!showAllMatches && matchedSkillsRef.current) {
            const rect = matchedSkillsRef.current.getBoundingClientRect();
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const targetPosition = rect.top + scrollTop;
            
            setShowAllMatches(true);
            
            setTimeout(() => {
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }, 50);
        } else {
            setShowAllMatches(false);
        }
    };

    const handleToggleGaps = () => {
        if (!showAllGaps && missingSkillsRef.current) {
            const rect = missingSkillsRef.current.getBoundingClientRect();
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const targetPosition = rect.top + scrollTop;
            
            setShowAllGaps(true);
            
            setTimeout(() => {
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }, 50);
        } else {
            setShowAllGaps(false);
        }
    };

    // Main analysis function
    const handleAnalyze = async (selectedProgram, selectedCareer) => {
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

            // Fetch AI recommendations
            const aiResponse = await fetch(`${API_BASE}/api/recommend`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    job_title: selectedCareer?.label,
                    curriculum_title: selectedProgram?.label,
                    missing_skills: data.gaps,
                    coverage_score: data.coverage_score,
                    relevance_score: data.relevance_score
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

    return {
        // State
        showResults,
        setShowResults,
        results,
        loading,
        error,
        recommendation,
        recLoading,
        isAiOpen,
        setIsAiOpen,
        showAllGaps,
        showAllMatches,
        
        // Refs
        summaryRef,
        matchedSkillsRef,
        missingSkillsRef,
        
        // Actions
        handleAnalyze,
        handleToggleMatches,
        handleToggleGaps
    };
};

export default useAnalysis;
