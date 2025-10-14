#!/usr/bin/env python3
import os
import sys
import json
import time
import socket
import requests
import urllib3
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from argus.utils.util import clean_domain_input, ensure_directory_exists, write_to_file
from argus.config.settings import DEFAULT_TIMEOUT, RESULTS_DIR, EXPORT_SETTINGS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console = Console()
TEAL = "#2EC4B6"

HEAD_SIGS = {
    "cloudflare": ("Server","cloudflare"),
    "akamai":     ("X-Akamai",""),
    "sucuri":     ("x-sucuri-id",""),
    "imperva":    ("X-CDN","imperva"),
    "incapsula":  ("X-CDN","Incapsula"),
    "aws-shield": ("x-amz-cf-id",""),
    "f5":         ("Server","f5")
}
ACTIVE_METHODS = ("TRACE","OPTIONS","PUT","DELETE")

def banner():
    bar = "=" * 44
    console.print(f"[{TEAL}]{bar}")
    console.print("[cyan]         Argus – Advanced Firewall Detection")
    console.print(f"[{TEAL}]{bar}\n")

def probe(url: str, timeout: int):
    try:
        return requests.get(url, timeout=timeout, verify=False)
    except:
        return None

def banner_grab(ip: str, port: int, timeout: int) -> str:
    try:
        s = socket.create_connection((ip, port), timeout)
        s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
        data = s.recv(160)
        s.close()
        return data.decode(errors="ignore")
    except:
        return ""

def run(target: str, threads: int, opts: dict):
    banner()
    timeout = int(opts.get("timeout", DEFAULT_TIMEOUT))
    url = target if "://" in target else f"https://{target}"
    dom = clean_domain_input(url)

    console.print(f"[white]* Probing [cyan]{url}[/cyan][/white]")
    r = probe(url, timeout)
    if not r:
        console.print("[red]✖ Target not reachable[/red]")
        return

    detections = set()

    for waf, (hdr, value) in HEAD_SIGS.items():
        hv = r.headers.get(hdr, "")
        if hv and (not value or value.lower() in hv.lower()):
            detections.add(waf)

    if r.status_code == 403:
        detections.add("403‑Forbidden (WAF?)")
    if r.elapsed.total_seconds() > 5:
        detections.add("Slow response (>5s)")

    body = (r.text or "").lower()
    if "captcha" in body or "access denied" in body:
        detections.add("Challenge/CAPTCHA")

    soup = BeautifulSoup(r.text or "", "html.parser")
    if soup.find(id="challenge") or soup.find("form", {"id": "cf-challenge-form"}):
        detections.add("JS challenge (Cloudflare‑style)")

    for p in ("/wp-admin","/phpmyadmin","/admin"):
        rp = probe(url.rstrip("/") + p, timeout)
        if rp and rp.status_code in (401, 403):
            detections.add(f"Blocked path {p}")

    for m in ACTIVE_METHODS:
        try:
            rp = requests.request(m, url, timeout=timeout, verify=False)
            if rp.status_code in (400, 405, 501):
                detections.add(f"{m} blocked")
        except:
            pass

    for port in (80, 443):
        b = banner_grab(dom, port, timeout)
        if "mod_security" in b.lower():
            detections.add("ModSecurity")

    result = ", ".join(sorted(detections)) or "No obvious WAF"
    table = Table(title=f"Firewall Detection – {dom}", header_style="bold white")
    table.add_column("Result", style="cyan")
    table.add_column("Details", overflow="fold")
    table.add_row(
        result,
        "Passive + active probes,\n"
        "header signatures, verb fuzzing,\n"
        "timing & content analysis"
    )
    console.print(table)
    console.print("[green]* Firewall detection completed[/green]")

    if EXPORT_SETTINGS.get("enable_txt_export"):
        out = os.path.join(RESULTS_DIR, dom)
        ensure_directory_exists(out)
        record_console = Console(record=True, width=console.width)
        record_console.print(table)
        txt = record_console.export_text()
        write_to_file(os.path.join(out, "firewall_detection.txt"), txt)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("[red]✖ No target provided. Please pass a domain or URL.[/red]")
        sys.exit(1)

    tgt = sys.argv[1]
    thr = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 1
    opts = {}
    if len(sys.argv) > 3:
        try:
            opts = json.loads(sys.argv[3])
        except json.JSONDecodeError:
            console.print("[yellow][!] Warning: could not parse JSON options, using defaults[/yellow]")

    run(tgt, thr, opts)
