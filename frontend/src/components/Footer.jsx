import { ScanLine, Code } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-gray-900 mt-auto">
      <div className="h-px bg-gradient-to-r from-transparent via-primary-500 to-transparent" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 sm:gap-6">
          {/* Logo + tagline */}
          <div>
            <div className="flex items-center gap-2.5 mb-3">
              <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg">
                <ScanLine className="w-4 h-4 text-white" />
              </div>
              <span className="text-base font-bold text-white">SkinScan</span>
            </div>
            <p className="text-sm text-gray-400 leading-relaxed">
              AI-powered skin condition detection for educational purposes.
            </p>
          </div>

          {/* Tech stack */}
          <div className="sm:text-center">
            <div className="flex items-center gap-1.5 sm:justify-center mb-3">
              <Code className="w-4 h-4 text-gray-400" />
              <span className="text-sm font-medium text-gray-300">Built With</span>
            </div>
            <div className="flex flex-wrap gap-2 sm:justify-center">
              {['DINOv2', 'PyTorch', 'FastAPI', 'React'].map((tech) => (
                <span
                  key={tech}
                  className="px-2.5 py-1 text-xs font-medium text-gray-300 bg-gray-800 rounded-md border border-gray-700"
                >
                  {tech}
                </span>
              ))}
            </div>
          </div>

          {/* Disclaimer */}
          <div className="sm:text-right">
            <p className="text-xs text-gray-500 leading-relaxed">
              This tool is for educational and demonstration purposes only.
              It should not be used for actual medical diagnosis. Always consult
              a qualified healthcare provider.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
