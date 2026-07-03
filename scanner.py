import ipaddress
import socket
import requests
from concurrent.futures import ThreadPoolExecutor


def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def _check_port(args):
    ip, port, timeout = args
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        result = s.connect_ex((ip, port))
        return port if result == 0 else None
    finally:
        s.close()


def scan_ports(ip, start_port=1, end_port=1024, timeout=0.5, max_workers=100):
    ports = range(start_port, end_port + 1)
    open_ports = []
    # Use a thread pool to check many ports concurrently to avoid very long waits
    with ThreadPoolExecutor(max_workers=min(max_workers, len(range(start_port, end_port + 1)))) as ex:
        args_iter = ((ip, p, timeout) for p in ports)
        for res in ex.map(_check_port, args_iter):
            if res:
                open_ports.append(res)
    open_ports.sort()
    return open_ports


def get_geo_info(ip):
    try:
        url = f'http://ip-api.com/json/{ip}'
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get('status') == 'success':
            return {
                'country': data.get('country', 'Unknown'),
                'city': data.get('city', 'unknown'),
                'isp': data.get('isp', 'Unknown'),
                'lat': data.get('lat', 0),
                'lon': data.get('lon', 0),
                'timezone': data.get('timezone', 'Unknown')
            }
        else:
            return {'error': 'Could not fetch geo info'}
    except requests.RequestException as e:
        return {'error': str(e)}


def full_scan(ip, port_range=(1, 1024)):
    if not is_valid_ip(ip):
        return {'error': f'{ip} is not a valid Ip address'}

    open_ports = scan_ports(ip, port_range[0], port_range[1])
    geo = get_geo_info(ip)

    return {
        'ip': ip,
        'open_ports': open_ports,
        # use consistent key name expected by other modules
        'geo_info': geo
    }

