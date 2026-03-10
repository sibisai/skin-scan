export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 py-8 mt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <p className="text-sm text-gray-500 mb-2">
            Built with PyTorch, FastAPI, and React
          </p>
          <p className="text-xs text-gray-400">
            This tool is for educational and demonstration purposes only. 
            It should not be used for actual medical diagnosis.
          </p>
        </div>
      </div>
    </footer>
  );
}
