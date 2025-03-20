import re
import requests
import urllib.parse
from Crypto.Cipher import AES
import os

COOKIE_CACHE_FILE = "cookie_cache.txt"

def to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def solve_js_challenge(html):
    # Parse key (a), iv (b), ciphertext (c) từ HTML
    a_match = re.search(r'a\s*=\s*toNumbers\("([0-9a-f]+)"\)', html)
    b_match = re.search(r'b\s*=\s*toNumbers\("([0-9a-f]+)"\)', html)
    c_match = re.search(r'c\s*=\s*toNumbers\("([0-9a-f]+)"\)', html)

    if not (a_match and b_match and c_match):
        raise Exception("Không tìm thấy key/iv/ciphertext trong HTML.")

    key = to_bytes(a_match.group(1))
    iv = to_bytes(b_match.group(1))
    ciphertext = to_bytes(c_match.group(1))

    # Giải mã AES-CBC
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext)

    # InfinityFree tạo cookie từ toHex(plaintext)
    cookie_value = plaintext.hex()
    return cookie_value

def load_cached_cookie():
    if os.path.exists(COOKIE_CACHE_FILE):
        with open(COOKIE_CACHE_FILE, "r") as f:
            cookie_val = f.read().strip()
            if cookie_val:
                return cookie_val
    return None
def save_cookie(cookie_val):
    with open(COOKIE_CACHE_FILE, "w") as f:
        f.write(cookie_val)

def bypass_infinityfree(url, params):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }

    session = requests.Session()
    cached_cookie = load_cached_cookie()
    if cached_cookie:
        print(f"Thử dùng cookie cache: {cached_cookie}")
        resp_try = session.get(url, params=params, headers=headers, cookies={"__test": cached_cookie})
        if "__test=" not in resp_try.text and "Javascript" not in resp_try.text:
            print("Bypass thành công bằng cookie đã lưu.")
            return resp_try.status_code, resp_try.text
        else:
            print("Cookie cached không dùng được, sẽ giải mã key mới.")
    # Request đầu tiên để lấy JS challenge
    response = session.get(url, params=params, headers=headers)
    html = response.text

    # Nếu có JS challenge
    if "__test=" in html:
        # Parse & giải mã cookie
        cookie_val = solve_js_challenge(html)
        print(f"Đã lấy cookie __test = {cookie_val}")
        save_cookie(cookie_val)  # Lưu lại cookie cho lần sau
        # Gửi request lần hai với cookie
        cookies = {
            "__test": cookie_val
        }
        response_2 = session.get(url, params=params, headers=headers, cookies=cookies)
        return response_2.status_code, response_2.text
    else:
        # Không bị challenge, trả về luôn
        return response.status_code, response.text
# data = "tai_khoan:user02mat_khau:pass02"
# if __name__ == "__main__":
#     target_url = "http://nguyengiang2603-1.infinityfreeapp.com/project/recieve_json.php"
#     query_params = {
#         "text":{data},
#     }

#     status, content = bypass_infinityfree(target_url, query_params)
#     print(f"Status: {status}")
#     print(content)
