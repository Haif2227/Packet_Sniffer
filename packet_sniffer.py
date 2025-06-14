#!/usr/bin/env python
import scapy.all as scapy
import argparse
from scapy.layers import http
import signal
import sys
import os

# Global list to store captured packets
captured_packets = []

def get_interface():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", dest="interface", help="Specify interface on which to sniff")
    arguments = parser.parse_args()
    return arguments.interface

def spoof(iface):
    print(f"[*] Starting sniffing on interface: {iface}")
    try:
        scapy.sniff(iface=iface, store=False, prn=process_packet)
    except KeyboardInterrupt:
        handle_exit()

def process_packet(packet):
    # Store packet in the global list for saving later
    captured_packets.append(packet)

    # Construct a single-line summary
    line = f"Packet: {packet.summary()}"
    
    # Add HTTP Request details if present
    if packet.haslayer(http.HTTPRequest):
        try:
            host = packet[http.HTTPRequest].Host.decode(errors="ignore")
            path = packet[http.HTTPRequest].Path.decode(errors="ignore")
            line += f" | HTTP: {host}{path}"
        except Exception:
            line += " | HTTP: [Error decoding host/path]"
    
    # Add Raw data if present
    if packet.haslayer(scapy.Raw):
        try:
            raw_data = packet[scapy.Raw].load.decode("utf-8", errors="ignore")
            line += f" | Raw: {raw_data[:50]}..."  # Truncate to 50 chars
        except Exception:
            line += " | Raw: [Error decoding raw data]"

    # Print the single-line summary
    print(line)

def handle_exit():
    print("\n[!] Sniffing stopped. Do you want to save captured packets to 'capture/capture.pcap'? (y/n)")
    choice = input("> ").strip().lower()
    if choice == 'y':
        save_to_pcap()
    else:
        print("[!] Packets not saved. Exiting...")
    sys.exit(0)

def save_to_pcap():
    folder = "capture"
    os.makedirs(folder, exist_ok=True)  # Create folder if it doesn't exist
    filepath = os.path.join(folder, "capture.pcap")
    scapy.wrpcap(filepath, captured_packets)
    print(f"[+] Packets saved to {filepath}")

# Signal handler to catch Ctrl+C
signal.signal(signal.SIGINT, lambda sig, frame: handle_exit())

iface = get_interface()
if iface:
    spoof(iface)
else:
    print("Please specify a valid interface using -i or --interface")
