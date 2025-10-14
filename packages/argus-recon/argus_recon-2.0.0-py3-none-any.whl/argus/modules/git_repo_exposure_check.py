#!/usr/bin/env python3
import os, sys, json, requests, urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.table import Table
from argus.utils.util import clean_domain_input, ensure_directory_exists, write_to_file
from argus.config.settings import DEFAULT_TIMEOUT, RESULTS_DIR, EXPORT_SETTINGS
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
console = Console(); TEAL = "#2EC4B6"

DOT_GIT_PATHS = (
    "/.git/HEAD",
    "/.git/config",
    "/.git/index",
    "/.git/packed-refs",
    "/.git/description",
    "/.git/info/refs",
    "/.git/info/exclude",
    "/.git/logs/HEAD",
    "/.git/logs/refs/heads/master",
    "/.git/logs/refs/heads/main",
    "/.git/objects/info/packs",
    "/.git/objects/pack/pack-.pack",
    "/.git/objects/pack/pack-.idx",
    "/.git/refs/heads/master",
    "/.git/refs/heads/main",
    "/.git/refs/stash",
    "/.git/refs/remotes/origin/HEAD",
    "/.git/refs/remotes/origin/master",
    "/.git/refs/remotes/origin/main",
    "/.git/ORIG_HEAD",
    "/.git/FETCH_HEAD",
    "/.git/COMMIT_EDITMSG",
    "/.git/refs/tags/latest",
    "/.git/hooks/pre-commit.sample",
    "/.git/hooks/post-update.sample",
    "/.git/hooks/pre-rebase.sample",
    "/.git/hooks/pre-receive.sample",
    "/.git/hooks/update.sample",
    "/.gitignore",
    "/.gitmodules",
    "/.git/rr-cache",
    "/.git/svn/refs/heads/master",
    "/.git/svn/refs/remotes/origin/trunk",
    "/.git/branches",
    "/.git/refs/heads/develop",
    "/.git/refs/heads/release",
    "/.git/refs/heads/production",
    "/.git/refs/heads/staging",
    "/.git/refs/heads/hotfix",
    "/.git/refs/remotes/origin/develop"
)

def banner():
    bar = "="*44
    console.print(f"[{TEAL}]{bar}")
    console.print("[cyan]   Argus – Git Repository Exposure Check")
    console.print(f"[{TEAL}]{bar}")

def probe(url, t):
    try:
        r = requests.get(url, timeout=t, verify=False, allow_redirects=False)
        return r.status_code, len(r.content)
    except: return "ERR", 0

def run(target, threads, opts):
    banner()
    timeout = int(opts.get("timeout", DEFAULT_TIMEOUT))
    dom     = clean_domain_input(target)
    base    = f"https://{dom}"
    console.print(f"[white]* Probing {len(DOT_GIT_PATHS)} .git artefact paths on [cyan]{dom}[/cyan][/white]")

    rows = []
    with ThreadPoolExecutor(max_workers=threads) as pool:
        futs = {pool.submit(probe, base+p, timeout): p for p in DOT_GIT_PATHS}
        for f in as_completed(futs):
            p            = futs[f]
            code, size   = f.result()
            exposed_flag = "Yes" if isinstance(code,int) and code < 400 and size > 0 else "-"
            rows.append((p, str(code), str(size), exposed_flag))

    rdir = requests.get(base+"/.git/", timeout=timeout, verify=False, allow_redirects=False)
    if rdir.status_code == 200 and b"Index of" in rdir.content:
        rows.append(("/.git/ (listing)","200",str(len(rdir.content)),"Index"))

    tbl = Table(title=f".git Exposure – {dom}", header_style="bold white")
    for h in ("Path","Status","Bytes","Exposed?"): tbl.add_column(h, overflow="fold")
    for r in rows: tbl.add_row(*r)
    console.print(tbl)
    console.print("[green]* Git repo exposure check completed[/green]")

    if EXPORT_SETTINGS["enable_txt_export"]:
        out = os.path.join(RESULTS_DIR, dom); ensure_directory_exists(out)
        write_to_file(os.path.join(out, "git_exposure.txt"), tbl.__rich__())

if __name__ == "__main__":
    tgt  = sys.argv[1]
    thr  = int(sys.argv[2]) if len(sys.argv)>2 and sys.argv[2].isdigit() else 12
    opts = {}
    if len(sys.argv)>3:
        try: opts = json.loads(sys.argv[3])
        except: pass
    run(tgt, thr, opts)
