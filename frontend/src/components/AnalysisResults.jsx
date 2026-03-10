import { useState, useRef, useEffect } from 'react';
import { Download, Info, CheckCircle, AlertCircle, AlertTriangle } from 'lucide-react';
import clsx from 'clsx';
import { conditionDescriptions, modelInfo } from '../utils/sampleData';
import { generateAnalysisReport } from '../utils/generatePDF';

// Format class names for display (e.g., "notumor" -> "No Tumor", "glioma" -> "Glioma")
function formatClassName(name) {
  const formatMap = {
    // Brain tumor
    'notumor': 'No Tumor',
    'glioma': 'Glioma',
    'meningioma': 'Meningioma',
    'pituitary': 'Pituitary',
    // Pneumonia
    'normal': 'Normal',
    'pneumonia': 'Pneumonia',
    // Retinal OCT
    'cnv': 'CNV',
    'dme': 'DME',
    'drusen': 'Drusen',
    // Bone fracture
    'fractured': 'Fractured',
    'not fractured': 'Not Fractured',
  };

  const lower = name.toLowerCase();
  if (formatMap[lower]) {
    return formatMap[lower];
  }

  // Fallback: capitalize first letter of each word
  return name.split(' ').map(word =>
    word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
  ).join(' ');
}

// Get condition description
function getConditionDescription(prediction) {
  const lower = prediction.toLowerCase();
  return conditionDescriptions[lower] || null;
}

// Format confidence percentage - cap at 99.9% for medical appropriateness
function formatConfidence(prob) {
  const percentage = prob * 100;
  // Cap at 99.9% - no medical AI should claim 100% certainty
  if (percentage >= 99.95) {
    return '99.9';
  }
  return percentage.toFixed(1);
}

export default function AnalysisResults({
  result,
  originalImage,
  selectedModel,
  isExplaining,
  explanation
}) {
  const [heatmapOpacity, setHeatmapOpacity] = useState(50);
  const [showGradcamInfo, setShowGradcamInfo] = useState(false);
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  const canvasRef = useRef(null);
  const [originalImg, setOriginalImg] = useState(null);
  const [heatmapImg, setHeatmapImg] = useState(null);

  const { prediction, confidence, probabilities, images } = result || {};

  // Sort probabilities by value descending
  const sortedProbs = probabilities
    ? Object.entries(probabilities).sort(([, a], [, b]) => b - a)
    : [];

  const isPredictionCorrect = confidence > 0.7;
  const conditionDescription = prediction ? getConditionDescription(prediction) : null;

  // Load images for canvas blending
  useEffect(() => {
    if (originalImage) {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => setOriginalImg(img);
      img.src = originalImage;
    }
  }, [originalImage]);

  useEffect(() => {
    if (images?.heatmap) {
      const img = new Image();
      img.onload = () => setHeatmapImg(img);
      img.src = `data:image/png;base64,${images.heatmap}`;
    }
  }, [images?.heatmap]);

  // Draw blended image on canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !originalImg || !heatmapImg) return;

    const ctx = canvas.getContext('2d');
    const size = 300;
    canvas.width = size;
    canvas.height = size;

    // Draw original
    ctx.globalAlpha = 1;
    ctx.drawImage(originalImg, 0, 0, size, size);

    // Draw heatmap with opacity
    ctx.globalAlpha = heatmapOpacity / 100;
    ctx.drawImage(heatmapImg, 0, 0, size, size);

  }, [originalImg, heatmapImg, heatmapOpacity]);

  const handleDownload = async () => {
    if (isGeneratingPDF) return;

    setIsGeneratingPDF(true);
    try {
      const model = modelInfo[selectedModel] || { name: 'Medical Image Analysis' };

      await generateAnalysisReport({
        prediction,
        confidence,
        probabilities,
        conditionDescription: explanation || conditionDescription,
        modelName: model.name,
        originalImageSrc: originalImage,
        heatmapCanvas: canvasRef.current,
        formatClassName,
        formatConfidence,
      });
    } catch (error) {
      console.error('Failed to generate PDF:', error);
    } finally {
      setIsGeneratingPDF(false);
    }
  };

  if (!result) return null;

  return (
    <div className="space-y-4">
      {/* Disclaimer Banner */}
      <div className="flex items-center gap-3 px-4 py-3 bg-amber-50 border border-amber-200 rounded-lg">
        <AlertTriangle className="w-5 h-5 text-amber-500 flex-shrink-0" />
        <p className="text-sm text-amber-800">
          <span className="font-medium">Educational Demo:</span> This tool is not a substitute for professional medical diagnosis.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        {/* Prediction Header */}
        <div className={clsx(
          'px-6 py-4 border-b',
          isPredictionCorrect ? 'bg-success-50 border-success-100' : 'bg-warning-50 border-warning-100'
        )}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {isPredictionCorrect ? (
                <CheckCircle className="w-6 h-6 text-success-500 flex-shrink-0" />
              ) : (
                <AlertCircle className="w-6 h-6 text-warning-500 flex-shrink-0" />
              )}
              <div>
                <p className="text-sm text-gray-600">Prediction</p>
                <p className={clsx(
                  'text-xl font-bold',
                  isPredictionCorrect ? 'text-success-700' : 'text-warning-700'
                )}>
                  {formatClassName(prediction)}
                </p>
              </div>
            </div>

            <div className="text-right">
              <p className="text-sm text-gray-600">Confidence</p>
              <p className={clsx(
                'text-xl font-bold',
                isPredictionCorrect ? 'text-success-700' : 'text-warning-700'
              )}>
                {formatConfidence(confidence)}%
              </p>
            </div>
          </div>

          {/* Condition Description / AI Explanation */}
          <div className="mt-3">
            {isExplaining ? (
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <div className="w-4 h-4 border-2 border-gray-300 border-t-gray-600 rounded-full animate-spin" />
                Generating explanation...
              </div>
            ) : explanation ? (
              <p className="text-sm text-gray-600 leading-relaxed">
                {explanation}
              </p>
            ) : conditionDescription ? (
              <p className="text-sm text-gray-600 leading-relaxed">
                {conditionDescription}
              </p>
            ) : null}
          </div>
        </div>

        <div className="p-6">
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Visualization Section */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <h4 className="text-sm font-medium text-gray-700">Grad-CAM Visualization</h4>
                <button
                  onClick={() => setShowGradcamInfo(!showGradcamInfo)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <Info className="w-4 h-4" />
                </button>
              </div>

              {showGradcamInfo && (
                <div className="mb-3 p-3 bg-primary-50 rounded-lg text-xs text-primary-800">
                  <strong>What is Grad-CAM?</strong> Gradient-weighted Class Activation Mapping highlights
                  the regions of the image that most influenced the model's prediction.
                </div>
              )}

              {/* Side-by-side comparison */}
              <div className="grid grid-cols-2 gap-3 mb-3">
                {/* Original Image */}
                <div>
                  <p className="text-xs font-medium text-gray-500 mb-2 text-center">Original</p>
                  <div className="aspect-square bg-gray-900 rounded-lg overflow-hidden">
                    {originalImage && (
                      <img
                        src={originalImage}
                        alt="Original"
                        className="w-full h-full object-cover"
                      />
                    )}
                  </div>
                </div>

                {/* Blended Heatmap */}
                <div>
                  <p className="text-xs font-medium text-gray-500 mb-2 text-center">Heatmap Overlay</p>
                  <div className="aspect-square bg-gray-900 rounded-lg overflow-hidden flex items-center justify-center">
                    <canvas
                      ref={canvasRef}
                      className="w-full h-full object-cover"
                      style={{ imageRendering: 'auto' }}
                    />
                  </div>
                </div>
              </div>

              {/* Color Legend - directly under images */}
              <div className="flex items-center justify-center gap-2 text-xs text-gray-500 font-medium mb-4">
                <span>Low importance</span>
                <div className="w-24 h-1 rounded-full bg-gradient-to-r from-blue-500 via-yellow-400 to-red-500" />
                <span>High importance</span>
              </div>

              {/* Heatmap Controls */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-xs font-medium text-gray-600">
                    Heatmap Intensity
                  </label>
                  <span className="text-xs font-semibold text-primary-600">
                    {heatmapOpacity}%
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={heatmapOpacity}
                  onChange={(e) => setHeatmapOpacity(Number(e.target.value))}
                  className="slider"
                />
              </div>

              <style>{`
                .slider {
                  -webkit-appearance: none;
                  appearance: none;
                  width: 100%;
                  height: 6px;
                  background: #e5e7eb;
                  border-radius: 3px;
                  outline: none;
                  cursor: pointer;
                }
                .slider::-webkit-slider-thumb {
                  -webkit-appearance: none;
                  appearance: none;
                  width: 18px;
                  height: 18px;
                  border-radius: 50%;
                  background: #1570EF;
                  cursor: pointer;
                  border: 2px solid white;
                  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
                }
                .slider::-moz-range-thumb {
                  width: 18px;
                  height: 18px;
                  border-radius: 50%;
                  background: #1570EF;
                  cursor: pointer;
                  border: 2px solid white;
                  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
                }
              `}</style>
            </div>

            {/* Probabilities Section */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-3">Class Probabilities</h4>

              <div className="space-y-3">
                {sortedProbs.map(([className, prob]) => {
                  const percentage = formatConfidence(prob);
                  const isPredicted = className.toLowerCase() === prediction.toLowerCase();
                  const displayName = formatClassName(className);

                  return (
                    <div key={className}>
                      <div className="flex items-center justify-between mb-1.5">
                        <span className={clsx(
                          'text-sm font-medium',
                          isPredicted ? 'text-primary-700' : 'text-gray-700'
                        )}>
                          {displayName}
                          {isPredicted && (
                            <span className="ml-2 text-xs font-normal text-primary-500">
                              (Predicted)
                            </span>
                          )}
                        </span>
                        <span className={clsx(
                          'text-sm font-semibold',
                          isPredicted ? 'text-primary-700' : 'text-gray-600'
                        )}>
                          {percentage}%
                        </span>
                      </div>

                      <div className="w-full h-2.5 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className={clsx(
                            'h-full rounded-full transition-all duration-500 ease-out',
                            isPredicted ? 'bg-primary-500' : 'bg-gray-300'
                          )}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Download Report Button */}
              <div className="mt-6 flex justify-center">
                <button
                  onClick={handleDownload}
                  disabled={isGeneratingPDF}
                  className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-primary-600 border border-primary-200 rounded-lg hover:bg-primary-50 disabled:opacity-50 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  {isGeneratingPDF ? 'Generating...' : 'Download Report'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}