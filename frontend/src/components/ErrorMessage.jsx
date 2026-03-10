import { AlertTriangle, RefreshCw } from 'lucide-react';

export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className="bg-error-50 border border-error-200 rounded-xl p-6">
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0">
          <div className="w-10 h-10 bg-error-100 rounded-full flex items-center justify-center">
            <AlertTriangle className="w-5 h-5 text-error-500" />
          </div>
        </div>
        
        <div className="flex-1">
          <h4 className="text-sm font-semibold text-error-700 mb-1">
            Analysis Failed
          </h4>
          <p className="text-sm text-error-600 mb-4">
            {message || 'An error occurred while analyzing the image. Please try again.'}
          </p>
          
          {onRetry && (
            <button
              onClick={onRetry}
              className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-error-700 bg-error-100 hover:bg-error-200 rounded-lg transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
