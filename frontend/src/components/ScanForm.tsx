import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { startScan } from '../services/api';
import { Search } from 'lucide-react';

export default function ScanForm() {
  const [domain, setDomain] = useState('');
  const [bruteforce, setBruteforce] = useState(true);
  const [passive, setPassive] = useState(true);
  const [threads, setThreads] = useState(20);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!domain.includes('.')) {
      setError('Please enter a valid domain (e.g., example.com)');
      return;
    }

    setLoading(true);
    try {
      const res = await startScan(domain, { bruteforce, passive, threads });
      navigate(`/scan/${res.scan_id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to start scan');
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 shadow-xl">
      <h2 className="text-xl font-bold mb-4 text-emerald-400 flex items-center gap-2">
        <Search size={20} /> New Scan
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">Target Domain</label>
          <input
            type="text"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            placeholder="example.com"
            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white focus:outline-none focus:border-emerald-500"
            required
          />
        </div>
        
        <div className="flex gap-4">
          <label className="flex items-center gap-2 text-sm text-slate-300">
            <input
              type="checkbox"
              checked={bruteforce}
              onChange={(e) => setBruteforce(e.target.checked)}
              className="accent-emerald-500"
            />
            Brute-force
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-300">
            <input
              type="checkbox"
              checked={passive}
              onChange={(e) => setPassive(e.target.checked)}
              className="accent-emerald-500"
            />
            Passive (crt.sh)
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">Threads ({threads})</label>
          <input
            type="range"
            min="1"
            max="50"
            value={threads}
            onChange={(e) => setThreads(parseInt(e.target.value))}
            className="w-full accent-emerald-500"
          />
        </div>

        {error && <div className="text-red-400 text-sm">{error}</div>}

        <div className="text-xs text-slate-400 border-l-2 border-slate-500 pl-2">
          Warning: Only scan domains you own or have permission to test.
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2 px-4 rounded transition disabled:opacity-50"
        >
          {loading ? 'Starting...' : 'Start Scan'}
        </button>
      </form>
    </div>
  );
}
