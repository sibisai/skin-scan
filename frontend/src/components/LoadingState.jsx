import { Loader2 } from 'lucide-react';

export default function LoadingState({ imageUrl }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      <div className="p-8">
        <div className="flex flex-col items-center justify-center">
          {imageUrl && (
            <div className="relative mb-6">
              <div className="w-32 h-32 rounded-xl overflow-hidden border-2 border-primary-200">
                <img
                  src={imageUrl}
                  alt="Analyzing"
                  className="w-full h-full object-cover animate-pulse"
                />
              </div>
              
              {/* Scanning line effect */}
              <div className="absolute inset-0 overflow-hidden rounded-xl">
                <div className="absolute w-full h-1 bg-gradient-to-r from-transparent via-primary-400 to-transparent animate-scan" />
              </div>
            </div>
          )}
          
          <div className="flex items-center gap-3 mb-3">
            <Loader2 className="w-5 h-5 text-primary-500 animate-spin" />
            <span className="text-lg font-medium text-gray-900">Analyzing image...</span>
          </div>
          
          <p className="text-sm text-gray-500 text-center max-w-xs">
            Running deep learning model and generating Grad-CAM visualization
          </p>
        </div>
      </div>
      
      {/* Progress shimmer */}
      <div className="h-1 bg-gray-100 overflow-hidden">
        <div className="h-full bg-gradient-to-r from-primary-200 via-primary-500 to-primary-200 animate-shimmer" />
      </div>
      
      <style>{`
        @keyframes scan {
          0% { top: 0; opacity: 0; }
          50% { opacity: 1; }
          100% { top: 100%; opacity: 0; }
        }
        .animate-scan {
          animation: scan 1.5s ease-in-out infinite;
        }
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        .animate-shimmer {
          animation: shimmer 1.5s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
