import requests
import bs4

LAN_IP = '192.168.0.10'

__all__ = ['get_init_ip']

def get_init_ip():
    net_type = input('Using LAN or WAN?')

    if 'wan' in net_type.lower():
        soup = bs4.BeautifulSoup(requests.get('https://myip.com.tw/').text.replace('\n', ''), 'html.parser')
        host_ip = soup.find('h1').find('font').text
    else:
        host_ip = LAN_IP
    # CURRENT_IP = host_ip
    print(f'Current IP: {host_ip}')
    return host_ip
    # CURRENT_IP = None