import { Brain, Stethoscope, Eye, Bone } from 'lucide-react';

const modelIcons = [
  { id: 'brain_tumor', icon: Brain, label: 'Brain Tumor' },
  { id: 'pneumonia', icon: Stethoscope, label: 'Pneumonia' },
  { id: 'retinal_oct', icon: Eye, label: 'Retinal OCT' },
  { id: 'bone_fracture', icon: Bone, label: 'Bone Fracture' },
];

export default function Hero({ onSelectModel }) {
  return (
    <section className="bg-gradient-to-b from-primary-50 to-white py-12 sm:py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div className="flex justify-center gap-3 mb-6">
          {modelIcons.map(({ id, icon: Icon, label }) => (
            <button
              key={id}
              onClick={() => onSelectModel?.(id)}
              title={label}
              className="flex items-center justify-center w-11 h-11 rounded-xl bg-primary-100 hover:bg-primary-200 transition-all duration-200"
            >
              <Icon className="w-5 h-5 text-primary-600" />
            </button>
          ))}
        </div>

        <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
          AI-Powered Medical Image Analysis
        </h2>

        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Upload medical images for instant classification using deep learning models.
          Visualize model decisions with Grad-CAM explanations.
        </p>
      </div>
    </section>
  );
}