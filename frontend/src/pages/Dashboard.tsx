import { useEffect, useState } from 'react';
import { getStats, listScans } from '../services/api';
import type { Stats, ScanSummary } from '../types/scan';
import ScanForm from '../components/ScanForm';
import StatCard from '../components/StatCard';
import { Globe, Database, Network, Activity } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [recentScans, setRecentScans] = useState<ScanSummary[]>([]);

  useEffect(() => {
    getStats().then(setStats).catch(console.error);
    listScans().then(scans => setRecentScans(scans.slice(0, 5))).catch(console.error);
  }, []);

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total Scans" value={stats?.scans ?? '-'} icon={<Activity size={24} />} color="text-blue-400" />
        <StatCard label="DNS Records" value={stats?.dns_records ?? '-'} icon={<Database size={24} />} color="text-emerald-400" />
        <StatCard label="Subdomains" value={stats?.subdomains ?? '-'} icon={<Globe size={24} />} color="text-purple-400" />
        <StatCard label="IP Addresses" value={stats?.ips ?? '-'} icon={<Network size={24} />} color="text-orange-400" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1">
          <ScanForm />
        </div>
        
        <div className="lg:col-span-2 bg-slate-800 rounded-lg border border-slate-700 p-6">
          <h2 className="text-xl font-bold mb-4 text-emerald-400">Recent Scans</h2>
          {recentScans.length === 0 ? (
            <div className="text-slate-400 text-center py-8">No scans yet. Start one!</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-700 text-slate-400">
                    <th className="p-3">Domain</th>
                    <th className="p-3">Status</th>
                    <th className="p-3 hidden sm:table-cell">Started</th>
                    <th className="p-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {recentScans.map((scan) => (
                    <tr key={scan.id} className="border-b border-slate-700/50 hover:bg-slate-700/20">
                      <td className="p-3 font-medium">{scan.domain}</td>
                      <td className="p-3">
                        <span className={`px-2 py-1 rounded text-xs font-bold ${
                          scan.status === 'completed' ? 'bg-emerald-500/20 text-emerald-400' :
                          scan.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                          'bg-blue-500/20 text-blue-400'
                        }`}>
                          {scan.status}
                        </span>
                      </td>
                      <td className="p-3 text-slate-400 text-sm hidden sm:table-cell">
                        {new Date(scan.started_at).toLocaleString()}
                      </td>
                      <td className="p-3 text-right">
                        <Link to={`/scan/${scan.id}`} className="text-emerald-400 hover:text-emerald-300 font-medium text-sm">
                          View details &rarr;
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
