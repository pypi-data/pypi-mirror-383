#!/usr/bin/env python3
import os
import sys
import json
import requests
import uuid
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from tabulate import tabulate
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from argus.utils.util import clean_domain_input, ensure_directory_exists, write_to_file
from argus.config.settings import DEFAULT_TIMEOUT, EXPORT_SETTINGS, RESULTS_DIR
console = Console()
AWS_TEMPLATES = [
    "https://{b}.s3.amazonaws.com/",
    "https://{b}.s3-us-east-1.amazonaws.com/",
    "https://{b}.s3.eu-west-1.amazonaws.com/",
    "https://{b}.s3.ap-northeast-1.amazonaws.com/",
    "https://{b}.s3-sa-east-1.amazonaws.com/",
    "https://s3.amazonaws.com/{b}/"
]
AZURE_TEMPLATE = "https://{b}.blob.core.windows.net/?restype=container&comp=list"
GCP_TEMPLATE   = "https://storage.googleapis.com/storage/v1/b/{b}/o"
DO_TEMPLATE    = "https://{b}.nyc3.digitaloceanspaces.com/"
COMMON_BUCKET_WORDS = [
    "backup","backups","data","files","static","media","images","assets","logs","db","dump",
    "public","private","upload","uploads","download","downloads","archive","archives","tmp","temp"
]

def banner():
    console.print("[cyan]" + "="*40)
    console.print("[cyan]   Argus – Cloud Bucket Exposure")
    console.print("[cyan]" + "="*40)

def probe_bucket(url, timeout):
    try:
        r = requests.get(url, timeout=timeout, verify=False)
        size = len(r.content or b"")
        ct = r.headers.get("Content-Type","")
        return url, r.status_code, size, ct
    except:
        return url, "ERR", 0, "-"

def derive_buckets(domain):
    parts = domain.split(".")
    base = domain.replace(".","-")
    buckets = { base, parts[0] }
    for w in COMMON_BUCKET_WORDS:
        buckets.add(f"{base}-{w}")
        buckets.add(f"{parts[0]}-{w}")
        buckets.add(f"{w}-{parts[0]}")
    return list(buckets)[:200]

def run(target, threads, opts):
    banner()
    dom = clean_domain_input(target)
    timeout = int(opts.get("timeout", DEFAULT_TIMEOUT))
    buckets = derive_buckets(dom)
    console.print(f"[white]* Probing [cyan]{len(buckets)}[/cyan] bucket names with [yellow]{threads}[/yellow] threads[/white]")

    urls = []
    for b in buckets:
        for tpl in AWS_TEMPLATES + [AZURE_TEMPLATE, GCP_TEMPLATE, DO_TEMPLATE]:
            urls.append(tpl.format(b=b))

    rows = []
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(), console=console, transient=True) as prog:
        task = prog.add_task("Probing buckets…", total=len(urls))
        with ThreadPoolExecutor(max_workers=threads) as pool:
            futures = { pool.submit(probe_bucket, u, timeout): u for u in urls }
            for fut in as_completed(futures):
                url, code, size, ct = fut.result()
                access = (
                    "Public" if code == 200 and size > 0 else
                    "Forbidden" if code == 403 else
                    "NotFound" if code == 404 else
                    "Unknown"
                )
                rows.append((url, str(code), str(size), ct, access))
                prog.advance(task)

    console.print(f"[white]* Identified [green]{sum(1 for r in rows if r[4]=='Public')}[/green] publicly accessible buckets[/white]")
    table_str = tabulate(
        sorted(rows, key=lambda r:(r[4], r[1], -int(r[2]))),
        headers=["URL","Status","Bytes","Content-Type","Access"],
        tablefmt="grid"
    )
    console.print(table_str)
    console.print("[green]* Cloud bucket exposure scan completed[/green]")

    if EXPORT_SETTINGS.get("enable_txt_export"):
        out = os.path.join(RESULTS_DIR, dom)
        ensure_directory_exists(out)
        write_to_file(os.path.join(out, "cloud_bucket_exposure.txt"), table_str)

if __name__=="__main__":
    tgt = sys.argv[1] if len(sys.argv)>1 else ""
    thr = int(sys.argv[2]) if len(sys.argv)>2 and sys.argv[2].isdigit() else 10
    opts = {}
    if len(sys.argv)>3:
        try:
            opts = json.loads(sys.argv[3])
        except:
            pass
    run(tgt, thr, opts)
