import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Image as ImageIcon, X } from 'lucide-react';
import clsx from 'clsx';

export default function FileUploader({ onFileSelect, selectedFile, previewUrl, onClear }) {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.webp']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  if (selectedFile && previewUrl) {
    return (
      <div className="relative">
        <div className="border-2 border-gray-200 rounded-xl p-4 bg-gray-50">
          <div className="flex items-start gap-4">
            <div className="w-20 h-20 rounded-lg overflow-hidden bg-white border border-gray-200 flex-shrink-0">
              <img
                src={previewUrl}
                alt="Selected"
                className="w-full h-full object-cover"
              />
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {selectedFile.name}
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {(selectedFile.size / 1024).toFixed(1)} KB
                  </p>
                </div>
                
                <button
                  onClick={onClear}
                  className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              
              <div className="mt-2 flex items-center gap-1.5">
                <div className="w-4 h-4 bg-success-500 rounded-full flex items-center justify-center">
                  <svg className="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span className="text-xs text-success-700 font-medium">Ready to analyze</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      {...getRootProps()}
      className={clsx(
        'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200',
        isDragActive
          ? 'border-primary-500 bg-primary-50'
          : 'border-gray-300 hover:border-gray-400 bg-white'
      )}
    >
      <input {...getInputProps()} capture="environment" />
      
      <div className="flex flex-col items-center">
        <div className={clsx(
          'w-12 h-12 rounded-full flex items-center justify-center mb-4',
          isDragActive ? 'bg-primary-100' : 'bg-gray-100'
        )}>
          {isDragActive ? (
            <ImageIcon className="w-6 h-6 text-primary-600" />
          ) : (
            <Upload className="w-6 h-6 text-gray-500" />
          )}
        </div>
        
        <p className="text-sm text-gray-600 mb-1">
          <span className="font-semibold text-primary-600">Take a photo</span>
          {' '}or upload an image
        </p>

        <p className="text-xs text-gray-500">
          PNG, JPG up to 10MB
        </p>
      </div>
    </div>
  );
}
