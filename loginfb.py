import requests
from fastapi import FastAPI
app = FastAPI()
@app.get("/get-cookie")
def GetCookie(user: str, password: str, twofa: str):
    headers = {
        "authority": "mbasic.facebook.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://mbasic.facebook.com",
        "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": 'navigate',
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    }
    login = requests.get('https://mbasic.facebook.com/login/device-based/regular/login/?refsrc=deprecated&lwv=100&refid=8', headers=headers)
    html = login.text
    lsd = html.split('name="lsd" value="')[1].split('"')[0]
    jazoest = html.split('name="jazoest" value="')[1].split('"')[0]
    m_ts = html.split('name="m_ts" value="')[1].split('"')[0]
    li = html.split('name="li" value="')[1].split('"')[0]
    cookie = login.headers["Set-Cookie"].split(";")[0]
    headers.update({"cookie": cookie})
    data = {
        "lsd": lsd,
        "jazoest": jazoest,
        "m_ts": m_ts,
        "li": li,
        "try_number": "0",
        "unrecognized_tries": "0",
        "email": user,
        "pass": password,
        "login": "Đăng nhập",
        "bi_xrwh": "0",
    }
    html = requests.post('https://mbasic.facebook.com/login/device-based/regular/login/?refsrc=deprecated&lwv=100&refid=8', data=data, headers=headers)
    if "Mật khẩu bạn vừa nhập chưa chính xác" in html.text or 'Bạn sử dụng mật khẩu cũ.' in html.text:
        return {"status": "password error!", "cookie": None}
    cookie = html.headers["Set-Cookie"].split(";")[0]
    headers.update({"cookie": cookie})
    html = html.text
    if 'Nhập mã đăng nhập để tiếp tục' in html:
        fb_dtsg = html.split('name="fb_dtsg" value="')[1].split('"')[0]
        nh = html.split('name="nh" value="')[1].split('"')[0]
        jazoest = html.split('name="jazoest" value="')[1].split('"')[0]
        code = requests.get("http://2fa.live/tok/"+twofa).json()["token"]
        data = {
            "fb_dtsg": fb_dtsg,
            "jazoest": jazoest,
            "checkpoint_data": "",
            "approvals_code": code,
            "codes_submitted": "0",
            "submit[Submit Code]": "Gửi mã",
            "nh": nh,

        }
        fa = requests.post("https://mbasic.facebook.com/login/checkpoint/", data=data, headers=headers)
        cookie = fa.headers["Set-Cookie"].split(";")[0]
        headers.update({"cookie": cookie})
        if 'Mã đăng nhập bạn nhập không khớp với mã đã gửi đến điện thoại của bạn. Vui lòng kiểm tra số này và thử lại.' in fa.text:
            return {"status": "2fa error!", "cookie": None}
        data = {
            "fb_dtsg": fb_dtsg,
            "jazoest": jazoest,
            "checkpoint_data": "",
            "name_action_selected": "save_device",
            "submit[Continue]": "Tiếp tục",
            "nh": nh,
        }
        fa = requests.post("https://mbasic.facebook.com/login/checkpoint/", data=data, headers=headers)
        cookie = fa.headers["Set-Cookie"].split(";")[0]
        return cookie
        headers.update({"cookie": cookie})
        if 'Tài khoản của bạn tạm thời bị khóa' in fa.text:
            print("ff")
            data.pop('name_action_selected')
            fa = requests.post("https://mbasic.facebook.com/login/checkpoint/", data=data, headers=headers)
            cookie = fa.headers["Set-Cookie"].split(";")[0]
            headers.update({"cookie": cookie})
            data.pop('submit[Continue]')
            data.update({"submit[This was me]": "Đây là tôi"})
            fa = requests.post("https://mbasic.facebook.com/login/checkpoint/", data=data, headers=headers)
            cookie = fa.headers["Set-Cookie"].split(";")[0]
            headers.update({"cookie": cookie})
            data.pop('submit[This was me]')
            data.update({"name_action_selected": "save_device","submit[Continue]": "Tiếp tục",})
            fa = requests.post("https://mbasic.facebook.com/login/checkpoint/", data=data, headers=headers, allow_redirects=False)
            cookie = fa.cookies
            cookie = "c_user=%s;fr=%s;sb=%s;xs=%s;datr=%s"%(cookie["c_user"], cookie["fr"], cookie["sb"], cookie["xs"], cookie["datr"])
        else:
            fa = requests.post("https://mbasic.facebook.com/login/checkpoint/", data=data, headers=headers, allow_redirects=False)
            cookie = fa.cookies
            cookie = "c_user=%s;fr=%s;sb=%s;xs=%s;datr=%s"%(cookie["c_user"], cookie["fr"], cookie["sb"], cookie["xs"], cookie["datr"])
    return {"status": "Success", "cookie": cookie}
# print(GetCookie("100080271526422", "NgocLy3312183Huy9999", "O3MKPJE4YZ64SDY6IW6GOHBAFQ2TPGXT"))
