#!/usr/bin/env python3

import argparse
import base64
import datetime
import hashlib
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

URLS = [
    "https://github.com/sakha1370/OpenRay/raw/refs/heads/main/output/all_valid_proxies.txt",
    "https://raw.githubusercontent.com/sevcator/5ubscrpt10n/main/protocols/vl.txt",
    "https://raw.githubusercontent.com/yitong2333/proxy-minging/refs/heads/main/v2ray.txt",
    "https://raw.githubusercontent.com/acymz/AutoVPN/refs/heads/main/data/V2.txt",
    "https://raw.githubusercontent.com/miladtahanian/V2RayCFGDumper/refs/heads/main/config.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/V2RAY_RAW.txt",
    "https://github.com/Epodonios/v2ray-configs/raw/main/Splitted-By-Protocol/trojan.txt",
    "https://raw.githubusercontent.com/YasserDivaR/pr0xy/refs/heads/main/ShadowSocks2021.txt",
    "https://raw.githubusercontent.com/mohamadfg-dev/telegram-v2ray-configs-collector/refs/heads/main/category/vless.txt",
    "https://raw.githubusercontent.com/mheidari98/.proxy/refs/heads/main/vless",
    "https://raw.githubusercontent.com/youfoundamin/V2rayCollector/main/mixed_iran.txt",
    "https://raw.githubusercontent.com/mheidari98/.proxy/refs/heads/main/all",
    "https://github.com/Kwinshadow/TelegramV2rayCollector/raw/refs/heads/main/sublinks/mix.txt",
    "https://github.com/LalatinaHub/Mineral/raw/refs/heads/master/result/nodes",
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/refs/heads/main/sub",
    "https://github.com/MhdiTaheri/V2rayCollector_Py/raw/refs/heads/main/sub/Mix/mix.txt",
    "https://github.com/Epodonios/v2ray-configs/raw/main/Splitted-By-Protocol/vmess.txt",
    "https://github.com/MhdiTaheri/V2rayCollector/raw/refs/heads/main/sub/mix",
    "https://github.com/Argh94/Proxy-List/raw/refs/heads/main/All_Config.txt",
    "https://raw.githubusercontent.com/shabane/kamaji/master/hub/merged.txt",
    "https://raw.githubusercontent.com/wuqb2i4f/xray-config-toolkit/main/output/base64/mix-uri",
    "https://raw.githubusercontent.com/AzadNetCH/Clash/refs/heads/main/AzadNet.txt",
    "https://raw.githubusercontent.com/STR97/STRUGOV/refs/heads/main/STR.BYPASS#STR.BYPASS%F0%9F%91%BE",
    "https://raw.githubusercontent.com/V2RayRoot/V2RayConfig/refs/heads/main/Config/vless.txt",
]

# ========================= CONFIG =========================
GITHUB_OWNER = "nikita29a"
GITHUB_REPO = "FreeProxyList"
TARGET_DIR = "mirror"
COMMIT_MESSAGE = "Mirror upstream proxy sources"
MAX_WORKERS = 12


# =========================================================


def normalize(text: str) -> str:
    return text.replace("\r\n", "\n").rstrip() + "\n"


def sha1_line(text: str) -> str:
    return hashlib.sha1(normalize(text).encode()).hexdigest()


def safe_filename_from_url(url: str) -> str:
    return f"source_{sha1_line(url)[:10]}.txt"


def fetch_and_process(index: int, url: str) -> tuple[str, str]:
    r = requests.get(url, timeout=30)
    r.raise_for_status()

    seen = set()
    lines = []

    for line in r.text.splitlines():
        line = line.strip()
        if not line:
            continue

        h = sha1_line(line)
        if h not in seen:
            seen.add(h)
            lines.append(line)

    content = "\n".join(sorted(lines)) + "\n"
    filename = f"{index}.txt"
    return filename, content


def get_existing_github_file(path: str):
    token = os.getenv("GITHUB_TOKEN")
    api = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    r = requests.get(api, headers=headers)

    if r.status_code == 404:
        return None, None

    r.raise_for_status()

    data = r.json()
    content = base64.b64decode(data["content"]).decode()
    return data["sha"], content


def upload_file_to_github(path: str, content: str):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is not set")

    api = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    sha, existing_content = get_existing_github_file(path)

    if existing_content is not None:
        if normalize(existing_content) == normalize(content):
            print(f"[SKIP] {path} (unchanged)")
            return

    payload = {
        "message": COMMIT_MESSAGE,
        "content": base64.b64encode(content.encode()).decode(),
    }

    if sha:
        payload["sha"] = sha

    r = requests.put(api, headers=headers, json=payload)
    r.raise_for_status()


def parse_args():
    p = argparse.ArgumentParser(description="Mirror proxy sources to GitHub")
    p.add_argument("--dry-run", action="store_true", help="Do not upload to GitHub")
    return p.parse_args()


def main():
    print("=== sync_proxies run ===")
    print("UTC time:", datetime.datetime.now(datetime.UTC).isoformat())

    args = parse_args()

    os.makedirs(TARGET_DIR, exist_ok=True)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(fetch_and_process, i + 1, url): url
            for i, url in enumerate(URLS)
        }

        for future in as_completed(futures):
            url = futures[future]
            try:
                filename, content = future.result()
                target_path = f"{TARGET_DIR}/{filename}"

                if args.dry_run:
                    with open(target_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"[DRY] {url} → {target_path}")
                else:
                    upload_file_to_github(target_path, content)
                    print(f"[OK]  {url} → {target_path}")

            except Exception as e:
                print(f"[FAIL] {url}: {e}")


if __name__ == "__main__":
    main()
