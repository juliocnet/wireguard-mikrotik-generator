import os
import subprocess
import qrcode
from pathlib import Path

# Function to generate private and public keys
def generate_keys():
    private_key = subprocess.check_output(['wg', 'genkey']).strip().decode('utf-8')
    public_key = subprocess.check_output(['wg', 'pubkey'], input=private_key.encode()).strip().decode('utf-8')
    return private_key, public_key

# Function to generate peer keys based on a seed
def generate_peer_keys(seed):
    private_key = subprocess.check_output(['wg', 'genkey']).strip().decode('utf-8')
    public_key = subprocess.check_output(['wg', 'pubkey'], input=private_key.encode()).strip().decode('utf-8')
    return private_key, public_key

# Collect user input in Spanish
print("Seleccione el modo de operación:")
print("1. Crear configuración del servidor y los peers")
print("2. Crear solo configuración de los peers")
mode_option = input("Ingrese 1 o 2: ").strip()
mode = "server+peers" if mode_option == "1" else "peers-only"

server_ip = input("Ingrese la IP pública o FQDN del servidor WireGuard: ").strip()
port = input("Ingrese el puerto de WireGuard (por defecto 13231): ").strip() or "13231"
interface = input("Ingrese el nombre de la interfaz WireGuard (por defecto 'wireguard-server'): ").strip() or "wireguard-server"
subnet = input("Ingrese la subred de WireGuard (ejemplo: 10.10.10.0/24): ").strip() or "10.10.10.0/24"
subnet_mask = subnet.split('/')[-1]  # Extract the mask from the subnet
gateway_ip = input(f"Ingrese la IP de la puerta de enlace para la subred WireGuard (por defecto {subnet.rsplit('.', 1)[0]}.1/{subnet_mask}): ").strip() or f"{subnet.rsplit('.', 1)[0]}.1/{subnet_mask}"
start_ip_octet = int(input("Ingrese el último octeto inicial para los peers (ejemplo: 50): ").strip() or 50)
peer_count = int(input("Ingrese el número de peers a crear (por defecto 1): ").strip() or 1)
allowed_ips = input("Ingrese las IPs permitidas para los peers (por defecto 0.0.0.0/0): ").strip() or "0.0.0.0/0"
dns_servers = input("Ingrese los servidores DNS (por defecto 8.8.8.8,8.8.4.4): ").strip() or "8.8.8.8,8.8.4.4"

# Server keys
if mode == "server+peers":
    server_private_key = input("Ingrese la clave privada del servidor (dejar en blanco para generar): ").strip()
    if not server_private_key:
        server_private_key, server_public_key = generate_keys()
        print("Clave privada del servidor generada:", server_private_key)
        print("Clave pública del servidor generada:", server_public_key)
    else:
        server_public_key = subprocess.check_output(['wg', 'pubkey'], input=server_private_key.encode()).strip().decode('utf-8')
else:
    server_public_key = input("Ingrese la clave pública del servidor: ").strip()

# Create output directories
config_dir = Path("./wireguard-configs")
config_dir.mkdir(exist_ok=True)
qrcode_dir = config_dir / "qrcodes"
qrcode_dir.mkdir(exist_ok=True)

# Generate peer configurations and QR codes
peer_configs = []
mikrotik_commands = []

for i in range(peer_count):
    peer_ip = f"{subnet.rsplit('.', 1)[0]}.{start_ip_octet + i}/32"
    peer_private_key, peer_public_key = generate_peer_keys(i)

    # Generate peer configuration
    peer_config = f"""
[Interface]
PrivateKey = {peer_private_key}
Address = {peer_ip}
DNS = {dns_servers}

[Peer]
PublicKey = {server_public_key}
Endpoint = {server_ip}:{port}
AllowedIPs = {allowed_ips}
"""
    peer_filename = config_dir / f"peer_{start_ip_octet + i}.conf"
    with open(peer_filename, "w") as f:
        f.write(peer_config)
    peer_configs.append(peer_filename)

    # Generate QR code
    qr = qrcode.QRCode()
    qr.add_data(peer_config)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img.save(qrcode_dir / f"peer_{start_ip_octet + i}.png")

    # Add MikroTik commands
    mikrotik_commands.append(
        f"/interface/wireguard/peers/add allowed-address={peer_ip} interface={interface} public-key=\"{peer_public_key}\" comment=\"peer_{start_ip_octet + i}\""
    )

# Generate MikroTik configuration file
mikrotik_config_file = config_dir / "mikrotik_commands.rsc"
with open(mikrotik_config_file, "w") as f:
    if mode == "server+peers":
        f.write(f"/interface/wireguard/add listen-port={port} name={interface} private-key=\"{server_private_key}\"\n")
        f.write(f"/ip/address/add address={gateway_ip} interface={interface}\n")
        f.write(f"/ip/firewall/filter/add chain=input action=accept protocol=udp dst-port={port} comment=\"Allow WireGuard\" place-before=0\n")
        f.write(f"/ip/firewall/filter/add chain=forward action=accept src-address={subnet} comment=\"Allow WireGuard Subnet Forwarding\" place-before=0\n")
    f.write("\n".join(mikrotik_commands))

print(f"Archivos de configuración guardados en: {config_dir}")
print(f"Códigos QR guardados en: {qrcode_dir}")
print(f"Comandos de configuración MikroTik guardados en: {mikrotik_config_file}")
