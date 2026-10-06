import { useEffect, useState } from 'react';
import { listScans, deleteScan } from '../services/api';
import type { ScanSummary } from '../types/scan';
import { Link } from 'react-router-dom';
import { Trash2, Search } from 'lucide-react';

export default function History() {
  const [scans, setScans] = useState<ScanSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchScans();
  }, []);

  const fetchScans = async () => {
    setLoading(true);
    try {
      const data = await listScans();
      setScans(data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this scan?')) {
      try {
        await deleteScan(id);
        fetchScans();
      } catch (e) {
        console.error(e);
      }
    }
  };

  if (loading) return <div className="text-center py-10 text-slate-400">Loading history...</div>;

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
      <h1 className="text-2xl font-bold mb-6 text-emerald-400 flex items-center gap-2">
        <Search size={24} /> Scan History
      </h1>
      
      {scans.length === 0 ? (
        <div className="text-slate-400 text-center py-10">No scans found.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-700 text-slate-400 bg-slate-900/50">
                <th className="p-4 rounded-tl-lg">ID</th>
                <th className="p-4">Domain</th>
                <th className="p-4">Status</th>
                <th className="p-4">Date</th>
                <th className="p-4">Subdomains</th>
                <th className="p-4">IPs</th>
                <th className="p-4 rounded-tr-lg text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {scans.map((scan) => (
                <tr key={scan.id} className="border-b border-slate-700/50 hover:bg-slate-700/20">
                  <td className="p-4 text-slate-400">#{scan.id}</td>
                  <td className="p-4 font-medium text-white">{scan.domain}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      scan.status === 'completed' ? 'bg-emerald-500/20 text-emerald-400' :
                      scan.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                      'bg-blue-500/20 text-blue-400'
                    }`}>
                      {scan.status}
                    </span>
                  </td>
                  <td className="p-4 text-slate-400 text-sm">
                    {new Date(scan.started_at).toLocaleString()}
                  </td>
                  <td className="p-4 text-slate-300">{scan.subdomains_count}</td>
                  <td className="p-4 text-slate-300">{scan.ips_count}</td>
                  <td className="p-4 text-right">
                    <div className="flex items-center justify-end gap-3">
                      <Link to={`/scan/${scan.id}`} className="text-emerald-400 hover:text-emerald-300 font-medium text-sm">
                        View
                      </Link>
                      <button onClick={() => handleDelete(scan.id)} className="text-red-400 hover:text-red-300">
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
