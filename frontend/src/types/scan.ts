export interface DnsRecords {
  domain: string;
  records: Record<string, string[]>;
  total_records: number;
  errors: Record<string, string>;
}

export interface SubdomainItem {
  subdomain: string;
  ips: string[];
  source: string;
  resolved: boolean;
}

export interface SubdomainsData {
  domain: string;
  subdomains: SubdomainItem[];
  total: number;
  resolved_count: number;
  unresolved_count: number;
  wildcard: boolean;
}

export interface IpInfo {
  ip: string;
  reverse_dns?: string | null;
  asn?: string | null;
  asn_description?: string | null;
  organization?: string | null;
  network?: string | null;
  country?: string | null;
  private: boolean;
}

export interface WhoisInfo {
  registrar?: string;
  creation_date?: string;
  expiration_date?: string;
  updated_date?: string;
  name_servers?: string[];
  status?: string[];
  org?: string;
  country?: string;
}

export interface Scan {
  id: number;
  domain: string;
  status: 'running' | 'completed' | 'failed';
  started_at: string;
  completed_at?: string;
  duration_seconds?: number;
  error?: string;
  dns: DnsRecords;
  subdomains: SubdomainsData;
  ips: IpInfo[];
  whois?: WhoisInfo;
  email_security?: {
    spf: boolean;
    dmarc: boolean;
  };
  zone_transfer?: {
    vulnerable: boolean;
    nameserver?: string;
  };
  timings?: Record<string, number>;
}

export interface ScanSummary {
  id: number;
  domain: string;
  status: string;
  started_at: string;
  subdomains_count: number;
  ips_count: number;
}

export interface Progress {
  stage: string;
  percent: number;
  status: string;
}

export interface Stats {
  scans: number;
  subdomains: number;
  ips: number;
  dns_records: number;
}
