import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getScan } from '../services/api';
import type { Scan } from '../types/scan';
import ScanProgress from '../components/ScanProgress';
import { Download, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export default function ScanDetails() {
  const { id } = useParams<{ id: string }>();
  const [scan, setScan] = useState<Scan | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('summary');

  const fetchScan = async () => {
    try {
      const data = await getScan(Number(id));
      setScan(data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchScan();
  }, [id]);

  if (loading) return <div className="text-center py-10 text-slate-400">Loading scan details...</div>;
  if (!scan) return <div className="text-center py-10 text-red-400">Scan not found.</div>;

  if (scan.status === 'running') {
    return (
      <div className="max-w-3xl mx-auto mt-10">
        <h1 className="text-2xl font-bold mb-6 text-emerald-400">Scan in Progress: {scan.domain}</h1>
        <ScanProgress scanId={scan.id} onComplete={fetchScan} />
      </div>
    );
  }

  const dnsData = Object.entries(scan.dns?.records || {}).map(([type, records]) => ({
    type,
    count: records.length
  }));

  const subData = [
    { name: 'Resolved', value: scan.subdomains?.resolved_count || 0 },
    { name: 'Unresolved', value: scan.subdomains?.unresolved_count || 0 }
  ];
  const COLORS = ['#10b981', '#ef4444'];

  const timeData = Object.entries(scan.timings || {}).map(([stage, sec]) => ({
    stage,
    seconds: Number(sec.toFixed(2))
  }));

  return (
    <div className="space-y-6">
      <div className="bg-slate-800 rounded-lg border border-slate-700 p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">{scan.domain}</h1>
          <div className="flex gap-4 text-sm text-slate-400">
            <span>Status: <span className={scan.status === 'completed' ? 'text-emerald-400' : 'text-red-400'}>{scan.status}</span></span>
            <span>Duration: {scan.duration_seconds?.toFixed(1)}s</span>
            <span>Date: {new Date(scan.started_at).toLocaleString()}</span>
          </div>
        </div>
        <div className="flex gap-3">
          <a href={`/api/scans/${scan.id}/report?format=json`} download className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded transition">
            <Download size={16} /> JSON
          </a>
          <a href={`/api/scans/${scan.id}/report?format=html`} download className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded transition">
            <Download size={16} /> HTML Report
          </a>
        </div>
      </div>

      <div className="flex border-b border-slate-700 overflow-x-auto">
        {['summary', 'dns', 'subdomains', 'ips', 'whois'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-6 py-3 font-medium capitalize whitespace-nowrap transition ${
              activeTab === tab ? 'text-emerald-400 border-b-2 border-emerald-400' : 'text-slate-400 hover:text-white'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {activeTab === 'summary' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <h3 className="text-lg font-bold text-white mb-4">Security Overview</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-slate-900 rounded">
                  <span className="text-slate-300">SPF Record</span>
                  {scan.email_security?.spf ? <CheckCircle className="text-emerald-500" /> : <AlertTriangle className="text-red-500" />}
                </div>
                <div className="flex justify-between items-center p-3 bg-slate-900 rounded">
                  <span className="text-slate-300">DMARC Record</span>
                  {scan.email_security?.dmarc ? <CheckCircle className="text-emerald-500" /> : <AlertTriangle className="text-red-500" />}
                </div>
                <div className="flex justify-between items-center p-3 bg-slate-900 rounded">
                  <span className="text-slate-300">Zone Transfer (AXFR)</span>
                  {scan.zone_transfer?.vulnerable ? <AlertTriangle className="text-red-500" /> : <CheckCircle className="text-emerald-500" />}
                </div>
                <div className="flex justify-between items-center p-3 bg-slate-900 rounded">
                  <span className="text-slate-300">Wildcard DNS</span>
                  {scan.subdomains?.wildcard ? <Info className="text-blue-500" /> : <span className="text-slate-500">None</span>}
                </div>
              </div>
            </div>

            <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <h3 className="text-lg font-bold text-white mb-4">DNS Record Distribution</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={dnsData}>
                    <XAxis dataKey="type" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip cursor={{fill: '#334155'}} contentStyle={{backgroundColor: '#1e293b', borderColor: '#334155'}} />
                    <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <h3 className="text-lg font-bold text-white mb-4">Subdomain Resolution</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={subData} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                      {subData.map((_, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                    </Pie>
                    <Tooltip contentStyle={{backgroundColor: '#1e293b', borderColor: '#334155'}} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="flex justify-center gap-4 text-sm mt-4">
                  <span className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-emerald-500"></span> Resolved ({scan.subdomains?.resolved_count})</span>
                  <span className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-red-500"></span> Unresolved ({scan.subdomains?.unresolved_count})</span>
                </div>
              </div>
            </div>

            <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <h3 className="text-lg font-bold text-white mb-4">Scan Timings</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={timeData} layout="vertical" margin={{ left: 30 }}>
                    <XAxis type="number" stroke="#94a3b8" unit="s" />
                    <YAxis dataKey="stage" type="category" stroke="#94a3b8" />
                    <Tooltip cursor={{fill: '#334155'}} contentStyle={{backgroundColor: '#1e293b', borderColor: '#334155'}} />
                    <Bar dataKey="seconds" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'dns' && (
        <div className="bg-slate-800 rounded-lg border border-slate-700 p-6 overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-slate-700 text-slate-400">
                <th className="p-3">Type</th>
                <th className="p-3">Value</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(scan.dns?.records || {}).map(([type, values]) =>
                values.map((val, i) => (
                  <tr key={`${type}-${i}`} className="border-b border-slate-700/50 hover:bg-slate-700/20">
                    <td className="p-3 font-bold text-emerald-400">{type}</td>
                    <td className="p-3 text-slate-300 font-mono text-sm">{val}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'subdomains' && (
        <div className="bg-slate-800 rounded-lg border border-slate-700 p-6 overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-slate-700 text-slate-400">
                <th className="p-3">Subdomain</th>
                <th className="p-3">Status</th>
                <th className="p-3">IPs</th>
                <th className="p-3">Source</th>
              </tr>
            </thead>
            <tbody>
              {scan.subdomains?.subdomains?.map((sub, i) => (
                <tr key={i} className="border-b border-slate-700/50 hover:bg-slate-700/20">
                  <td className="p-3 text-white">{sub.subdomain}</td>
                  <td className="p-3">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${sub.resolved ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                      {sub.resolved ? 'Resolved' : 'NXDOMAIN'}
                    </span>
                  </td>
                  <td className="p-3 text-slate-300 text-sm font-mono">{sub.ips?.join(', ') || '-'}</td>
                  <td className="p-3 text-slate-400 text-sm">{sub.source}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'ips' && (
        <div className="bg-slate-800 rounded-lg border border-slate-700 p-6 overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-slate-700 text-slate-400">
                <th className="p-3">IP</th>
                <th className="p-3">Reverse DNS</th>
                <th className="p-3">ASN</th>
                <th className="p-3">Organization</th>
                <th className="p-3">Country</th>
              </tr>
            </thead>
            <tbody>
              {scan.ips?.map((ip, i) => (
                <tr key={i} className="border-b border-slate-700/50 hover:bg-slate-700/20">
                  <td className="p-3 text-white font-mono">{ip.ip}</td>
                  <td className="p-3 text-slate-300 text-sm">{ip.reverse_dns || '-'}</td>
                  <td className="p-3 text-slate-300 text-sm">{ip.asn || '-'}</td>
                  <td className="p-3 text-slate-300 text-sm">{ip.organization || '-'}</td>
                  <td className="p-3 text-slate-300 text-sm">{ip.country || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'whois' && (
        <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
          {scan.whois ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-slate-300">
              <div>
                <p className="mb-2"><strong className="text-white">Registrar:</strong> {scan.whois.registrar || '-'}</p>
                <p className="mb-2"><strong className="text-white">Created:</strong> {scan.whois.creation_date || '-'}</p>
                <p className="mb-2"><strong className="text-white">Expires:</strong> {scan.whois.expiration_date || '-'}</p>
                <p className="mb-2"><strong className="text-white">Updated:</strong> {scan.whois.updated_date || '-'}</p>
              </div>
              <div>
                <p className="mb-2"><strong className="text-white">Organization:</strong> {scan.whois.org || '-'}</p>
                <p className="mb-2"><strong className="text-white">Country:</strong> {scan.whois.country || '-'}</p>
                <p className="mb-2"><strong className="text-white">Status:</strong> {scan.whois.status?.join(', ') || '-'}</p>
                <p className="mb-2"><strong className="text-white">Name Servers:</strong></p>
                <ul className="list-disc pl-5">
                  {scan.whois.name_servers?.map((ns, i) => <li key={i}>{ns}</li>)}
                </ul>
              </div>
            </div>
          ) : (
            <div className="text-slate-400">No WHOIS data available.</div>
          )}
        </div>
      )}

    </div>
  );
}
