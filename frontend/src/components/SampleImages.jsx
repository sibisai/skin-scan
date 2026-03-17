import clsx from 'clsx';
import { sampleImages } from '../utils/sampleData';

export default function SampleImages({ model, selectedSample, onSelect }) {
  const samples = sampleImages[model] || [];

  return (
    <div>
      <h4 className="text-sm font-medium text-gray-700 mb-3">
        Try a sample image
      </h4>
      
      <div className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-6 gap-3">
        {samples.map((sample) => (
          <button
            key={sample.id}
            onClick={() => onSelect(sample)}
            className={clsx(
              'relative aspect-square rounded-lg overflow-hidden border-2 hover:-translate-y-0.5 hover:shadow-md transition-all duration-200',
              selectedSample?.id === sample.id
                ? 'border-primary-500 ring-4 ring-primary-500/20'
                : 'border-gray-200 hover:border-gray-300'
            )}
          >
            <img
              src={sample.path}
              alt={sample.label}
              className="w-full h-full object-cover"
              loading="lazy"
            />

            <span className="absolute bottom-1.5 left-1/2 -translate-x-1/2 bg-black/60 backdrop-blur-sm text-white text-[10px] font-medium px-2 py-0.5 rounded-full whitespace-nowrap">
              {sample.label}
            </span>

            {selectedSample?.id === sample.id && (
              <div className="absolute top-1.5 right-1.5 w-5 h-5 bg-primary-500 rounded-full flex items-center justify-center shadow-sm">
                <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
