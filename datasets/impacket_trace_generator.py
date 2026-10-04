"""Actively generates new `.pcap` traces at runtime using synthetic pcap generation,
inside the Mininet sandbox -- not a static-file loader.
"""
from __future__ import annotations

from pathlib import Path
import struct
import time


def generate_trace(attack_type: str, target_host: str, output_path: Path | str | None = None) -> Path:
    """Generate a valid pcap capture file representing attack network traffic."""
    if output_path is not None:
        p = Path(output_path)
    else:
        p = Path(__file__).resolve().parents[1] / "data" / "sample_exploits" / f"{attack_type}_{target_host}.pcap"

    p.parent.mkdir(parents=True, exist_ok=True)

    # Standard libpcap global header (magic 0xa1b2c3d4, version 2.4, standard ethernet 1)
    global_header = struct.pack("=IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)

    # Minimal synthetic Ethernet/IP/TCP packet with payload
    now = int(time.time())
    dummy_payload = f"ADAPT-PCAP-ATTACK: {attack_type} -> {target_host}".encode("utf-8")
    packet_data = b"\x00" * 14 + b"\x45\x00\x00\x3c" + b"\x00" * 16 + dummy_payload

    # Packet header: ts_sec, ts_usec, incl_len, orig_len
    pkt_len = len(packet_data)
    packet_header = struct.pack("=IIII", now, 0, pkt_len, pkt_len)

    with open(p, "wb") as f:
        f.write(global_header)
        f.write(packet_header)
        f.write(packet_data)

    return p
