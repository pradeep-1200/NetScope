import type { Scan, ScanSummary, Progress, Stats } from '../types/scan';

const API_BASE = '/api';

export const startScan = async (domain: string, options: any) => {
  const res = await fetch(`${API_BASE}/scans`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ domain, options })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
};

export const getScan = async (id: number): Promise<Scan> => {
  const res = await fetch(`${API_BASE}/scans/${id}`);
  if (!res.ok) throw new Error('Failed to fetch scan');
  return res.json();
};

export const getProgress = async (id: number): Promise<Progress> => {
  const res = await fetch(`${API_BASE}/scans/${id}/progress`);
  if (!res.ok) throw new Error('Failed to fetch progress');
  return res.json();
};

export const listScans = async (): Promise<ScanSummary[]> => {
  const res = await fetch(`${API_BASE}/scans`);
  if (!res.ok) throw new Error('Failed to fetch scans');
  return res.json();
};

export const deleteScan = async (id: number) => {
  const res = await fetch(`${API_BASE}/scans/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete scan');
  return res.json();
};

export const getStats = async (): Promise<Stats> => {
  const res = await fetch(`${API_BASE}/stats`);
  if (!res.ok) throw new Error('Failed to fetch stats');
  return res.json();
};
