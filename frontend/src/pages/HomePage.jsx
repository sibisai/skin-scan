import { Link } from 'react-router-dom';
import { Camera, ArrowRight, Shield } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="flex-1">
      {/* Hero Section */}
      <section className="bg-gradient-to-b from-primary-50 to-white py-16 sm:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
            SkinScan
          </h1>

          <p className="text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto mb-3">
            AI-powered skin condition detection from your phone.
          </p>

          <p className="text-sm text-gray-500 mb-8">
            Detects acne, eczema, fungal infections, psoriasis, scabies & healthy skin
          </p>

          <Link
            to="/analyze"
            className="inline-flex items-center gap-2 bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors"
          >
            <Camera className="w-5 h-5" />
            Start Scanning
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      {/* How it Works */}
      <section className="py-12 sm:py-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold text-center text-gray-900 mb-8">
            How It Works
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { step: '1', title: 'Take a Photo', desc: 'Use your phone camera to capture the affected skin area.' },
              { step: '2', title: 'Get Analysis', desc: 'AI analyzes the image and identifies potential conditions.' },
              { step: '3', title: 'See Explanation', desc: 'View highlighted areas showing what the AI detected.' },
            ].map(({ step, title, desc }) => (
              <div key={step} className="text-center">
                <div className="w-12 h-12 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
                  {step}
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
                <p className="text-gray-600 text-sm">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Disclaimer */}
      <section className="py-8">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-start gap-3 bg-amber-50 border border-amber-200 rounded-lg p-4">
            <Shield className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <p className="text-sm text-amber-800">
              <strong>Disclaimer:</strong> This tool is for educational purposes only. Always consult a dermatologist for proper diagnosis and treatment.
            </p>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-12 border-t border-gray-100">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 text-center">
            {[
              { value: '6', label: 'Conditions' },
              { value: '89%', label: 'Accuracy' },
              { value: '6,700+', label: 'Training Images' },
              { value: '<2s', label: 'Analysis Time' },
            ].map(({ value, label }) => (
              <div key={label}>
                <div className="text-2xl sm:text-3xl font-bold text-primary-600">{value}</div>
                <div className="text-sm text-gray-500">{label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
