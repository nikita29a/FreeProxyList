#!/usr/bin/env python3

import argparse
import base64
import datetime
import hashlib
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from cryptography.fernet import Fernet
import requests

ENCRYPTED_URLS = [
  "gAAAAABpgDj220v604h6Qi_EHRaireeK5yxRADbk86RsuWY9-XqmQ8CdJaYwJ5JKXSSr4mgAqktJqJccMbVeIK1U9wvc9hXnJUhx7Kw8AaN3K45Y5SWYEblD-lDOrbekl3Ap4XY2XLpq15BWQ1MfuBEBGMozOuohTBws5DgkFWPtMkdh214oxRLlSDSGTNySE4p5EImhM328",
  "gAAAAABpgDj26g9vJGzh_JzCEox8QSag3FucM2U-3g30h13NMppuj_OaDewggmaRHhefIuCY5L96bIpieY40QEEJH_uIrCGwNcXPcfPw0FN7O8QN-X3alGn776_U3PUch44UK4R6K32BwpwK0mdL1TjvWj3IvCmcLekbZ0ozJLnoeidHrEcnVGM=",
  "gAAAAABpgDj2MbJnQUNeVn4xGj52GDZHoZqjyEUBPaV0wxftlObeJJj7eEvH9j-1Kyhhe4xZIU5rkTFCGjcNn1Z4JcbE7CwkwOSLvU09bSMmz8p_dPkLFJA8D7B3qx6vScej5TNXxJc7g27pwAgaoej2j_lThUsMP7BVnaCIln_XJs2VRii8i0gBkJ89OwKzQ2czfpsCIp9J",
  "gAAAAABpgDj23J6hQWpHXmLqkdW3tgsG_KHp5X697Sxzd0jQpWAOR_yO2NC51oIyQ5cAQ6OcoKQeONaq_RmCYi0vmOMuormMSqw_iUDHBCCHqbj3zt1ytjnLdiuCnyISSwPxABr-0IAI0Y6al-qFJISaIqfIAglA_o3yRaxnAj__u8R6tHiYSTs=",
  "gAAAAABpgDj2q1dcmjTHsxlzkumBZfFbQyyjvJQf9378bhTsrXN0bvzc3o0bLDAY7xUK1m8JyjS_OJETta5Um-xFzQaFCrW4nnC9Be3ufzCG-LN_6zxAlhX2RBMaP4i-STfl8MGjfThv-yn0R4mYc6rPhQc2RzH18Lkj_CrPiLsGutQPma5eXKX1GbNPrFXwatmdIfTGW4UY",
  "gAAAAABpgDj2jZH6Xm4Dd15HfWAyiaD9YHChcZvAoT8rDhAlH5sNUDKVFaarG0b3RQQn600p_csKdwzOzvgN6UaL2EUAiso9Cgfo_PWqynEkClfkkqL-eQwWbncqA-cz7Cj6HeRdhu3c0705wDWrLjic4M5RIuqgKfG82SZkn5CXg4VcUw-WGtU=",
  "gAAAAABpgDj2pT9R0c1JuxtFZ-CanJRvf-86VET4eGEfHdwRaBsei85g_n6LB5L9qM88F4Od7sLpFzPGuhJPQFvctDUUu26b74S_y4uN6UQh7RwPBfUA5kiCObkrPRmVIhYBv_qCS_AENjZHGZ0jAd8dx1O-CE1Li9WOvRuSzWoeJYsCulqj4CuqKYCOeW1QeKfYpuwUA1vc",
  "gAAAAABpgDj2UVARwBnyxp7HUlBpeg4QDGLi6KM0gXP9EyZrn26Pk01P3tezMjAqICtNDoYUALOQc1yQuP-rbqBE-Q0Qj7uQUDjzbctk2dqu30v_9DtN9JCIoYeefrFNsYhroKOuGOUDRI13QLc2bAzIb-6p6uOjkOg8WI0nWamjMoLREhAC-AA3jBA6jpi7zr2c0r9CcEnk",
  "gAAAAABpgDj2XNttyU7gLo-G2qQKR2rf8GDlHNlZO5L4D0uWnJnr-OGGjtbMHXDvZ3InWX0f11OOob-dEcBtB6Ao8R3OUr09OTCJ4oQRp7ZFdswUqOVuIWSkJKttzwN4Y50KW9M4EUnmZAA-MrmIAHo47fNrHMHbjiJ8bMqDsHXNGMM369tvXEnpBlpoYgFP-xUEVO_L0UGax-17qCeL4xr2SQujAC22p_Ml1uumi6UUWiMFvO_4k5U=",
  "gAAAAABpgDj2q-gQXAMU78SZAuTjJ0UF1RApiuLrd0tXZ3nV-n1WuGlxxTXe_fEHIrNmitz0Ry6AJ1RQBGGhg_rEQkXXUvnD2vkYXg__gGQwCQYVCTncwGgy1nRnF_b6o7NZTMy8p9h3L1lBmQjpcON70w99fAw_Ja_APG17Q2R5jPW2Tfr-hg4=",
  "gAAAAABpgDj2E1w3ndtdd_4BhjA4Fok_wVjpWIJTd9UcUqcg46SgUJpUGFEBbdzdIrWmYB6Pdr8ExTYDeeFbFQfOV3BMivzPGpYMASiD8o1VTKoXeK49ko0H3Uk8lv9ffCT-A74HYEpvWbuYKmKQnPNcRDqhborSvMJqsO5Y4GFx8pJ85Z-g2A0uggZAxXafmeNZJJoyqMhX",
  "gAAAAABpgDj2GtHO4SXXAgZgyIDNTp9Do92y9yLAZ2sG73hKzc6j5a7yv1UMjKcjytma-2GvZjz4hw0sfQ7mqrRBfpgAsf8J2If5NekyhRi4D-8jRGxjSBzGZoqdRKLA3gbFz7Ln4B-cb3RXiCslZIvQHtC67ggtr5m-NyqWW4J9SMPh83xPLgI=",
  "gAAAAABpgDj2hf3NhwEfMNMOsDdCCtClgGWpkK8yNI4M45i3BRzFeLBNApLVs3ZXtIbzLSD7uw85slAVVCpq2yNqaPW2avQJmeteERJPy3_9JY2bODkjfGM8ErNRnKtdXupZTiEvIfYocMLw6EoFz6ccc_-7kCscsWukQc21plMBjEvDTHU-7aOgWMkDfVmPgez5fbgoWUZR",
  "gAAAAABpgDj24wvNI6sY2giG10XEN0ZWle7rjcLuodMMciLNYglZ6eynLRIcMl2rfitfPXMNFjlXlNxUjGrNUv6D2CVFKbgXVzNhK-sIfeysQWThWM-06mwe-LyKhiCS43mCb_j00Bl-wtUTpEB6kvDC9tUeS3lZj8mmA44HwsSrPB5v0o5H8o0=",
  "gAAAAABpgDj2jdfhRDLkoOg1kef32nDWIbfayrdykilL9v6LT5_BFS0VniE-UdYHNb_EgvJF9CyQ_vFniU8rRWLepubv81KjK3qvKHehq0OE4CPfc6oRZhhVKXE_RIp5rBTimWiA73_i0G0VYPd02OQY7cKbIvnNJvs-aGUQc-8o4tbotcGPH1k=",
  "gAAAAABpgDj2Hxd_SVqeeUFEwydIMIaVHu-_IDY17YZQQ431q995YLzgj-i5pJgcQ0jZvFAeyK95q2KiklQiTcZpBBNe4sj8_gNK4n3JtFmi8t1lHndvheqm23v4nuu8VPwJXGLDbL4zQncMbG0jwKXjoixbJa1uPGH4w93L86yq3BT2kFtvxzUh6x2GsvCnZeq3zBVtrFbn",
  "gAAAAABpgDj2kQWWVF0xB3oSMsrTeqTPRy3Kqk1wKmDCOURf2Y2ajau5KfVTCr0CHRPs6asCqmdgj_dAumjz6yywIOeKqT4rffzSLoy9jkpg04GmlbFbCGsx4uY1qUVeSpC0Kj5dPrGquzfF0sqsjKCRP9jOj39urw7YKedselFAM9YDjUUzTgNms86r8WhQKvjG4u7nqJ9Q",
  "gAAAAABpgDj2Xtxh_pqPqSlaS4xruxdz5sPhtdsyw2C9P9Qg1aHOeoGFBfagcCpkKOWvzfBu0vd91X4ZCJ6Unqu4iGnmMK2VQaIot7VRK6UEtvnBcvkLR2K7IDKDxaQe-UB0fC7RP_UkrMRjxvRCO8Iq68aLueIBzim8yz8-TgnSAOjvBY7PfJg=",
  "gAAAAABpgDj2u-1gsrOLNfkaUH0sB_HH_y4Q9604Oy8rfXps5kO4e8eYi18WiryJ-qMG0HHg1Tvs9DJRsMMYyG4tZvfMdPVjm-hkeMjBzd3FYtDHDX7wxpyqRXc8JpydQ8Pzngorse-3vWLHpS1Kg-ioJnwfGlrsV8ocDaL-GF8g6rQf3LNw8cU=",
  "gAAAAABpgDj2Z7oJ2a3ccVsvY7NUnZjA-_2F9Gg3kQTn6goh15hoGtiE1CXrY4o-E7AlV11U0Wy6oxRnks6cylwt6iPyj0sjNTrzumwLo2Ht5aB_lllVs9-t3KfDLVzBH59MmPS3e4pnDpFjolhV5VbVS7xzFGWEp2x4Mp7Eams5aq5CDF3Yh4U=",
  "gAAAAABpgDj2w0v13NLVk4gJsm5PuW2QCGR1brOLunGDF92lcpIX3stpxHy915743Yx7ZyC24dMwyRyfGl-wfaYL1eueDfqJko2Wp3G49JNm4ErIr84HrX8EcXOli4HiGO46yay3RqPXpIuu5fDQnMoXCFdqF_o1i8ZOIhXaOWXhRSglXzkx_4Kia6A8lVtmOu3zOV1g5bxV",
  "gAAAAABpgDj2nX8SGn6mEeH25236SNUGj5sUqrFWirVWRMIsVVPkggORpj3ytu3XatlOu66rSTXP73lwJpI9aV6BhW_DGVWelIhe_44FoRgALjp0_rKprHveg7bso2zRZsz_R1oJ6Yx2vBBRHlHZ_lM29MiPCcPsSAkg8cpjP6XHOZaFmNY5qxU=",
  "gAAAAABpgDj2jHEdE9lqwR67Z4b0U07paPZOhk-o7S0zTjmkrMjezghUmHMRLNLIIlf9QCKL2Wcu6GmE5rkw6LIrS323BSmzPXQOnT4o-Itio_avCJHkuxzBVBFb1RsHlkJ2qiytwJZfswkulMCczE5IFlJ-qTEYxAGfhKo2CqfP-Och0iUxYVze6LRu50mN0iazxibwW0UINiOe5dmZJVOFgYCS1a4dew==",
  "gAAAAABpgDj2gkhitioX9BHPE_5gcOlLBjasaiz_Q7oj4pFT6XvFlYxeDLKIHaaytdWqRnHcPDV25OX2A8Nm90YhwAJGDJ18WcPOw-29cmD6rs0uqXOkiuRkKg5qnKaQ045GQNYfkXU7XaKNRkY_cvgWiy8l4p1U3Ukn3wnrf854LhrT5gYikY9K4KnCj5pnzYEgdS4XKg5S"
]

# ========================= CONFIG =========================
GITHUB_OWNER = "nikita29a"
GITHUB_REPO = "FreeProxyList"
TARGET_DIR = "mirror"
COMMIT_MESSAGE = "Mirror upstream proxy sources"
MAX_WORKERS = 12


# =========================================================
def load_urls() -> list[str]:
    key = os.getenv("URLS_SECRET_KEY")
    if not key:
        raise RuntimeError("URLS_SECRET_KEY is not set")

    f = Fernet(key.encode())
    return [f.decrypt(u.encode()).decode() for u in ENCRYPTED_URLS]


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
    urls = load_urls()
    print(f"Loaded {len(urls)} URLs")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(fetch_and_process, i + 1, url): url
            for i, url in enumerate(urls)
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
