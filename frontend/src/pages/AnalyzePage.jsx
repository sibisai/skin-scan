import { useState, useCallback, useRef } from 'react';
import SampleImages from '../components/SampleImages';
import FileUploader from '../components/FileUploader';
import AnalysisResults from '../components/AnalysisResults';
import LoadingState from '../components/LoadingState';
import ErrorMessage from '../components/ErrorMessage';
import { useImageAnalysis } from '../hooks/useImageAnalysis';
import { ArrowRight } from 'lucide-react';

export default function AnalyzePage() {
  // Hardcoded to skin_disease - no model selection needed
  const selectedModel = 'skin_disease';

  const [selectedSample, setSelectedSample] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  const step2Ref = useRef(null);
  const resultsRef = useRef(null);

  const { analyze, reset, isAnalyzing, isExplaining, result, explanation, error } = useImageAnalysis();

  // Handle sample image selection
  const handleSampleSelect = useCallback((sample) => {
    setSelectedSample(sample);
    setUploadedFile(null);
    setPreviewUrl(sample.path);
    reset();
    setTimeout(() => {
      step2Ref.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
  }, [reset]);

  // Handle file upload
  const handleFileSelect = useCallback((file) => {
    setUploadedFile(file);
    setSelectedSample(null);
    reset();
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    setTimeout(() => {
      step2Ref.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
    return () => URL.revokeObjectURL(url);
  }, [reset]);

  // Clear selection
  const handleClear = useCallback(() => {
    setUploadedFile(null);
    setSelectedSample(null);
    setPreviewUrl(null);
    reset();
  }, [reset]);

  // Run analysis
  const handleAnalyze = useCallback(async () => {
    if (!previewUrl) return;

    let file = uploadedFile;

    if (selectedSample && !uploadedFile) {
      try {
        const response = await fetch(selectedSample.path);
        const blob = await response.blob();
        file = new File([blob], `${selectedSample.id}.jpg`, { type: 'image/jpeg' });
      } catch (err) {
        console.error('Failed to load sample image:', err);
        return;
      }
    }

    if (file) {
      analyze(selectedModel, file);
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    }
  }, [previewUrl, uploadedFile, selectedSample, selectedModel, analyze]);

  const hasSelection = selectedSample || uploadedFile;

  return (
    <div className="flex-1">
      {/* Hero Section */}
      <section className="bg-gradient-to-b from-primary-50 to-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Skin Analysis
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Upload or take a photo of a skin area for AI-powered analysis.
          </p>
        </div>
      </section>

      {/* Main Content */}
      <div className="py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">

          {/* Step 1: Image Selection */}
          <section className="mb-10">
            <div className="flex items-center gap-3 mb-4">
              <span className="flex items-center justify-center w-7 h-7 bg-primary-100 text-primary-700 text-sm font-semibold rounded-full">
                1
              </span>
              <h3 className="text-lg font-semibold text-gray-900">Select Image</h3>
            </div>

            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
              <FileUploader
                onFileSelect={handleFileSelect}
                selectedFile={uploadedFile}
                previewUrl={uploadedFile ? previewUrl : null}
                onClear={handleClear}
              />

              <div className="relative my-6">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-200" />
                </div>
                <div className="relative flex justify-center">
                  <span className="px-3 bg-white text-sm text-gray-500">or try a sample</span>
                </div>
              </div>

              <SampleImages
                model={selectedModel}
                selectedSample={selectedSample}
                onSelect={handleSampleSelect}
              />
            </div>
          </section>

          {/* Step 2: Analyze / Results */}
          <section ref={step2Ref} className="scroll-mt-6">
            {/* Analyze Button */}
            {hasSelection && !result && !isAnalyzing && (
              <div className="mb-10">
                <div className="flex items-center gap-3 mb-4">
                  <span className="flex items-center justify-center w-7 h-7 bg-primary-100 text-primary-700 text-sm font-semibold rounded-full">
                    2
                  </span>
                  <h3 className="text-lg font-semibold text-gray-900">Analyze</h3>
                </div>
                <button
                  onClick={handleAnalyze}
                  disabled={isAnalyzing}
                  className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-xl shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Analyze Skin
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>
            )}

            {/* Results */}
            {(isAnalyzing || result || error) && (
              <div ref={resultsRef} className="scroll-mt-6">
                <div className="flex items-center gap-3 mb-4">
                  <span className="flex items-center justify-center w-7 h-7 bg-primary-100 text-primary-700 text-sm font-semibold rounded-full">
                    3
                  </span>
                  <h3 className="text-lg font-semibold text-gray-900">Results</h3>
                </div>

                {isAnalyzing && <LoadingState imageUrl={previewUrl} />}

                {error && !isAnalyzing && (
                  <ErrorMessage message={error} onRetry={handleAnalyze} />
                )}

                {result && !isAnalyzing && (
                  <AnalysisResults
                    result={result}
                    originalImage={previewUrl}
                    selectedModel={selectedModel}
                    isExplaining={isExplaining}
                    explanation={explanation}
                  />
                )}
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
