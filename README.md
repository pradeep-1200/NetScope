# NetScope: A DNS Enumeration and Network Footprinting Framework

NetScope is an educational and modular reconnaissance framework designed to automate the initial phases of footprinting a target domain. It integrates DNS enumeration, subdomain bruteforcing, passive certificate transparency lookups, IP/Network analysis, and WHOIS information retrieval into a clean, modern dashboard.

**Disclaimer: This tool is for educational and authorized security testing purposes only. Only scan domains you own or have explicit permission to test.**

## Features
- **DNS Enumeration:** Gathers A, AAAA, MX, NS, TXT, SOA, SRV, CAA, and CNAME records.
- **Subdomain Discovery:** Combines multithreaded wordlist bruteforcing with passive crt.sh lookups, and automatically filters wildcard/catch-all domains.
- **IP Footprinting:** Collects resolved IPs and performs reverse DNS, ASN, and organization mapping.
- **Security Checks:** Checks for zone transfer (AXFR) misconfigurations and validates SPF/DMARC email security records.
- **Reporting:** Automatically generates standalone JSON and HTML reports.
- **Dashboard:** A React-based web interface to manage and visualize scan results.

## Architecture

```text
+-------------------+       +-----------------------+       +-------------------+
|   React Frontend  | <---> |   FastAPI Backend     | <---> |   SQLite Database |
+-------------------+       +-----------------------+       +-------------------+
                                  |
                                  +--> DNS Enum (dnspython)
                                  +--> Subdomain Enum (bruteforce, crt.sh)
                                  +--> IP & Network Analysis (ipwhois, socket)
                                  +--> WHOIS Lookup (python-whois)
                                  +--> Report Generation (Jinja2)
```

## Tech Stack
| Component | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI |
| Database | SQLite (Built-in) |
| Frontend | React, TypeScript, Vite, Tailwind CSS, Recharts |
| Reporting | Jinja2 |

## Directory Structure
- `backend/`: Core python logic, REST API, and modules
- `frontend/`: React + Vite web dashboard
- `database/`: SQLite database storage
- `output/`: Generated HTML and JSON reports
- `tests/`: Pytest suite

## Installation

### Prerequisites
- Python 3.11+
- Node.js 18+

### Setup
1. Clone the repository.
2. Initialize the backend:
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
3. Initialize the frontend:
   ```powershell
   cd frontend
   npm install
   ```

## Running the Application

### Option 1: One-Click Start
Run the provided `start.ps1` script to launch both the backend and frontend simultaneously:
```powershell
.\start.ps1
```

### Option 2: Manual Start
**Backend:**
```powershell
cd backend
.\venv\Scripts\uvicorn main:app --reload
```
**Frontend:**
```powershell
cd frontend
npm run dev
```

## CLI Usage
You can also run scans directly from the terminal without the frontend:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python cli.py scan example.com --report html
python cli.py history
```

## API Endpoints
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/scans` | Start a new scan |
| GET | `/api/scans` | List all past scans |
| GET | `/api/scans/{id}` | Get full results of a scan |
| GET | `/api/scans/{id}/progress` | Get progress of a running scan |
| DELETE | `/api/scans/{id}` | Delete a scan |
| GET | `/api/scans/{id}/report` | Download JSON or HTML report |
| GET | `/api/stats` | Get dashboard stats |

## Future Improvements
- Integrate more passive OSINT sources (e.g., Shodan, Censys).
- Add scheduled monitoring for continuous reconnaissance.
- Implement basic port scanning on discovered IPs.
