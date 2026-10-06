import { type ReactNode } from 'react';

interface StatCardProps {
  label: string;
  value: string | number;
  icon: ReactNode;
  color?: string;
}

export default function StatCard({ label, value, icon, color = 'text-emerald-400' }: StatCardProps) {
  return (
    <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 flex items-center gap-4">
      <div className={`p-3 rounded-full bg-slate-900 ${color}`}>
        {icon}
      </div>
      <div>
        <div className="text-sm text-slate-400">{label}</div>
        <div className="text-2xl font-bold text-white">{value}</div>
      </div>
    </div>
  );
}
