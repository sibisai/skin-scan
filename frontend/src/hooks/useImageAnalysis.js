import { useState, useCallback } from 'react';
import { analyzeImage, generateExplanation } from '../utils/api';

export function useImageAnalysis() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isExplaining, setIsExplaining] = useState(false);
  const [result, setResult] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [error, setError] = useState(null);

  const analyze = useCallback(async (modelName, imageFile) => {
    setIsAnalyzing(true);
    setIsExplaining(false);
    setResult(null);
    setExplanation(null);
    setError(null);

    try {
      // First call - get prediction + gradcam (fast)
      const analysisResult = await analyzeImage(modelName, imageFile);
      setResult(analysisResult);
      setIsAnalyzing(false);

      // Second call - get explanation (slower, runs in background)
      setIsExplaining(true);
      try {
        const comparisonImage = analysisResult.images?.comparison;
        if (comparisonImage) {
          const explanationResult = await generateExplanation(
            modelName,
            analysisResult.prediction,
            analysisResult.confidence,
            comparisonImage
          );
          setExplanation(explanationResult.explanation);
        }
      } catch (explainError) {
        console.error('Explanation failed:', explainError);
        // Don't set error - explanation is optional
      } finally {
        setIsExplaining(false);
      }

    } catch (err) {
      setError(err.message || 'Analysis failed');
      setIsAnalyzing(false);
      setIsExplaining(false);
    }
  }, []);

  const reset = useCallback(() => {
    setIsAnalyzing(false);
    setIsExplaining(false);
    setResult(null);
    setExplanation(null);
    setError(null);
  }, []);

  return {
    analyze,
    reset,
    isAnalyzing,
    isExplaining,
    result,
    explanation,
    error,
  };
}