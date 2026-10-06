import { useEffect, useState } from 'react';
import { getProgress } from '../services/api';
import type { Progress } from '../types/scan';

interface ScanProgressProps {
  scanId: number;
  onComplete?: () => void;
}

const STAGES = ['validation', 'dns', 'security', 'subdomains', 'ips', 'whois', 'completed'];

export default function ScanProgress({ scanId, onComplete }: ScanProgressProps) {
  const [progress, setProgress] = useState<Progress | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    let interval: ReturnType<typeof setInterval>;

    const poll = async () => {
      try {
        const data = await getProgress(scanId);
        if (mounted) {
          setProgress(data);
          if (data.status === 'completed' || data.status === 'failed') {
            clearInterval(interval);
            if (onComplete) onComplete();
          }
        }
      } catch (err: any) {
        if (mounted) setError(err.message);
      }
    };

    poll();
    interval = setInterval(poll, 1500);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [scanId, onComplete]);

  if (error) return <div className="text-red-400">Error: {error}</div>;
  if (!progress) return <div className="text-slate-400 animate-pulse">Loading progress...</div>;

  return (
    <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
      <div className="flex justify-between mb-2">
        <span className="text-slate-300 font-medium capitalize">
          {progress.status === 'failed' ? 'Scan Failed' : `Stage: ${progress.stage}`}
        </span>
        <span className="text-emerald-400 font-bold">{progress.percent}%</span>
      </div>
      <div className="w-full bg-slate-900 rounded-full h-4 overflow-hidden border border-slate-700">
        <div
          className={`h-full transition-all duration-500 ${progress.status === 'failed' ? 'bg-red-500' : 'bg-emerald-500'}`}
          style={{ width: `${progress.percent}%` }}
        />
      </div>
      <div className="flex justify-between mt-2 text-xs text-slate-500 hidden md:flex">
        {STAGES.map((s) => (
          <span key={s} className={progress.stage === s ? 'text-emerald-400 font-bold' : ''}>
            {s}
          </span>
        ))}
      </div>
    </div>
  );
}
