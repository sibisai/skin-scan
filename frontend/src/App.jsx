import { Routes, Route } from 'react-router-dom';
import Navigation from './components/shared/Navigation';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import AnalyzePage from './pages/AnalyzePage';

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navigation />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/analyze" element={<AnalyzePage />} />
      </Routes>
      <Footer />
    </div>
  );
}

export default App;
