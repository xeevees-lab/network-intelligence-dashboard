import ipaddress
import socket
import requests

def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def scan_ports(ip, start_port=1, end_port=1024, timeout=0.5):
    open_ports =[]
    for port in range(start_port, end_port + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((ip, port))
        if result == 0:
           open_ports.append(port)
           print(f' Port {port}: OPEN')
        s.close()
    return open_ports


if __name__ == '__main__':
    ip = '127.0.0.1'   # scan your own machine first
    print(f'Scanning {ip}...')
    ports = scan_ports(ip, start_port=1, end_port=100)
    print('Open ports:', ports)

def get_geo_info(ip):
    try:
        url = f'http://ip-api.com/json/{ip}'
        response = requests.get(url, timeout=5)
        data = response.json()

        if data['status'] =='success':
            return {
                'country': data.get('country', 'Unknown'),
                'city': data.get('city', 'unknown'),
                'isp': data.get('isp', 'Unknown'),
                'lat': data.get('lat', 0),
                'lon': data.get('lon', 0),
                'timezone': data.get('timezone', 'Unknown')
            }
        else: return {'error': 'Could not fetch geo info'}
    except requests.RequestException as e:
        return {'error': str(e)}

geo = get_geo_info('8.8.8.8')

print('Geo Info:', geo)

def full_scan(ip, port_range=(1, 1024)):
    if not is_valid_ip(ip):
        return{'error': f'{ip} is not a valid Ip address'}
    print(f'Staring scan of {ip}...')
    
    #Port Scan
    open_ports = scan_ports(ip, port_range[0], port_range[1])

    #Geo Info
    geo = get_geo_info(ip)

    return {
        'ip': ip,
        'open_ports': open_ports,
        'geo': geo
    }

