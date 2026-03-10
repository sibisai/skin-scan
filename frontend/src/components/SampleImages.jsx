import clsx from 'clsx';
import { sampleImages } from '../utils/sampleData';

export default function SampleImages({ model, selectedSample, onSelect }) {
  const samples = sampleImages[model] || [];

  return (
    <div>
      <h4 className="text-sm font-medium text-gray-700 mb-3">
        Try a sample image
      </h4>
      
      <div className="grid grid-cols-4 sm:grid-cols-4 gap-3">
        {samples.map((sample) => (
          <button
            key={sample.id}
            onClick={() => onSelect(sample)}
            className={clsx(
              'group relative aspect-square rounded-lg overflow-hidden border-2 transition-all duration-200',
              selectedSample?.id === sample.id
                ? 'border-primary-500 ring-2 ring-primary-500/20'
                : 'border-gray-200 hover:border-gray-300'
            )}
          >
            <img
              src={sample.path}
              alt={sample.label}
              className="w-full h-full object-cover"
              loading="lazy"
            />
            
            {/* Hover overlay */}
            <div className={clsx(
              'absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent',
              'flex items-end justify-center p-2 transition-opacity duration-200',
              selectedSample?.id === sample.id ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
            )}>
              <span className="text-xs font-medium text-white text-center leading-tight">
                {sample.label}
              </span>
            </div>

            {/* Selected checkmark */}
            {selectedSample?.id === sample.id && (
              <div className="absolute top-1.5 right-1.5">
                <div className="w-5 h-5 bg-primary-500 rounded-full flex items-center justify-center shadow-sm">
                  <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
