import { Link } from 'react-router-dom';
import {
  Camera,
  ArrowRight,
  Shield,
  Sparkles,
  Cpu,
  Eye,
  Layers,
  Target,
  Database,
  Zap,
} from 'lucide-react';

export default function HomePage() {
  return (
    <div className="flex-1">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary-50 via-white to-primary-25 py-20 sm:py-28">
        <div className="absolute top-[-6rem] right-[-6rem] w-80 h-80 bg-primary-200/30 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-[-6rem] left-[-6rem] w-96 h-96 bg-primary-200/30 rounded-full blur-3xl pointer-events-none" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <span className="inline-flex items-center gap-1.5 bg-primary-100 text-primary-700 rounded-full px-3.5 py-1 text-xs font-medium mb-6">
            <Sparkles className="w-3.5 h-3.5" />
            AI-Powered Skin Analysis
          </span>

          <h1 className="text-5xl sm:text-6xl font-extrabold bg-gradient-to-r from-gray-900 via-primary-800 to-gray-900 bg-clip-text text-transparent mb-4">
            SkinScan
          </h1>

          <p className="text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto mb-3">
            AI-powered skin condition detection from your phone.
          </p>

          <p className="text-sm text-gray-500 mb-8">
            Detects acne, eczema, fungal infections, psoriasis, scabies & healthy skin
          </p>

          <div className="flex items-center justify-center gap-4 flex-wrap">
            <Link
              to="/analyze"
              className="btn-primary"
            >
              <Camera className="w-5 h-5" />
              Start Scanning
              <ArrowRight className="w-4 h-4" />
            </Link>

            <a
              href="#how-it-works"
              className="btn-ghost"
              onClick={(e) => {
                e.preventDefault();
                document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' });
              }}
            >
              Learn More
            </a>
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section id="how-it-works" className="py-12 sm:py-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold text-center text-gray-900 mb-8">
            How It Works
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { step: '1', title: 'Take a Photo', desc: 'Use your phone camera to capture the affected skin area.', icon: Camera },
              { step: '2', title: 'Get Analysis', desc: 'AI analyzes the image and identifies potential conditions.', icon: Cpu },
              { step: '3', title: 'See Explanation', desc: 'View highlighted areas showing what the AI detected.', icon: Eye },
            ].map(({ step, title, desc, icon: Icon }) => (
              <div
                key={step}
                className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 hover:shadow-md hover:border-primary-100 transition-all duration-300 text-center"
              >
                <div className="relative w-14 h-14 mx-auto mb-4">
                  <div className="w-14 h-14 bg-gradient-to-br from-primary-500 to-primary-700 text-white rounded-2xl shadow-md flex items-center justify-center">
                    <Icon className="w-6 h-6" />
                  </div>
                  <span className="absolute -top-1 -right-1 w-5 h-5 bg-white text-primary-600 text-xs font-bold rounded-full shadow-sm flex items-center justify-center">
                    {step}
                  </span>
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
              { value: '6', label: 'Conditions', icon: Layers },
              { value: '89%', label: 'Accuracy', icon: Target },
              { value: '6,700+', label: 'Training Images', icon: Database },
              { value: '<2s', label: 'Analysis Time', icon: Zap },
            ].map(({ value, label, icon: Icon }) => (
              <div
                key={label}
                className="bg-white rounded-xl p-5 border border-gray-100 shadow-xs hover:shadow-sm transition-shadow duration-200"
              >
                <Icon className="w-5 h-5 text-primary-400 mb-2 mx-auto" />
                <div className="text-3xl sm:text-4xl font-extrabold text-primary-600">{value}</div>
                <div className="text-sm text-gray-500">{label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
