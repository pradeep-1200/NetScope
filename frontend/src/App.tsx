import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import ScanDetails from './pages/ScanDetails';
import History from './pages/History';
import { Activity } from 'lucide-react';

function Navbar() {
  return (
    <nav className="bg-slate-800 border-b border-slate-700 p-4">
      <div className="container mx-auto flex items-center justify-between">
        <Link to="/" className="flex items-center text-emerald-400 font-bold text-xl gap-2">
          <Activity size={24} />
          NetScope
        </Link>
        <div className="flex gap-4">
          <Link to="/" className="text-slate-300 hover:text-white transition">Dashboard</Link>
          <Link to="/history" className="text-slate-300 hover:text-white transition">History</Link>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-900 text-slate-200 font-sans">
        <Navbar />
        <main className="container mx-auto p-4 md:p-6 lg:p-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/scan/:id" element={<ScanDetails />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
