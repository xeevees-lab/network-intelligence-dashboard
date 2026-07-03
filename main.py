from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import os
from datetime import datetime
from scanner import full_scan, is_valid_ip
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
import csv
import io

app =FastAPI(
    title="Network Intelligence Dashboard",
    description=" Scans IPs, find open ports, get geo info",
    version='1.0.0'
)

app.mount('/static', StaticFiles(directory='static'), name='static')

#To allow frontend talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

RESULTS_FILE  ='results.json'

def load_history():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_result(result):
    history = load_history()
    result['timestamp'] = datetime.now().isoformat()
    history.append(result)
    with open (RESULTS_FILE, 'w') as f:
        json.dump(history, f, indent=2)

@app.get('/')
def read_root():
    return FileResponse('static/index.html')

@app.get('/health')
def health_check():
    return {'status': 'ok', 'message': 'Network Dashboard is running'}

@app.get('/scan')
def scan_ip(ip: str, start_port: int =1, end_port: int = 1024):
    if not is_valid_ip(ip):
        raise HTTPException(status_code=400, detail='Invalid IP address')
    result = full_scan(ip, port_range=(start_port, end_port))
    save_result(result)
    return result

@app.get('/history')
def get_history():
    return load_history()

@app.get('/stats')
def get_stats():
    history = load_history()
    if not history:
        return {'total_scans': 0}
    all_ports =[]
    countries =[]

    for scan in history:
        all_ports.extend(scan.get('open_ports', []))
        geo = scan.get('geo_info', {})
        if 'country' in geo:
            countries.append(geo['country'])

    #Count port frequencies
    port_counts = {}
    for p in all_ports:
        port_counts[p] = port_counts.get(p, 0) + 1

    top_ports = sorted(port_counts, key=lambda x: x[1], reverse=True)[:5]

    return {
        'total_scans': len(history),
        'total_open_ports_found': len(all_ports),
        'most_common_ports': top_ports,
        'countries_scanned': list(set(countries))
    }

@app.get('/export')
def export_csv():
    history = load_history()
    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow(['IP', 'Open Ports', 'Country', 'City', 'ISP', 'Timestamp'])

    # Data rows
    for scan in history:
        geo = scan.get('geo', {})
        writer.writerow([
            scan.get('ip', ''),
            ', '.join(str(p) for p in scan.get('open_ports', [])),
            geo.get('country', ''),
            geo.get('city', ''),
            geo.get('isp', ''),
            scan.get('timestamp', '')
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename=scan_history.csv'}
    )