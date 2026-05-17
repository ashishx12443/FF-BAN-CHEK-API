from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

REQUEST_TIMEOUT = (5, 12)


def check_ban_info(target_id):
    ban_url = f'https://ff.garena.com/api/antihack/check_banned?lang=en&uid={target_id}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'authority': 'ff.garena.com',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'referer': 'https://ff.garena.com/en/support/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'x-requested-with': 'B6FksShzIgjfrYImLpTsadjS86sddhFH',
    }

    try:
        response = requests.get(ban_url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        ban_data = response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Ban status API request failed: {e}"}
    except ValueError:
        return {"error": "Ban status API returned invalid JSON"}

    if ban_data.get("status") != "success" or "data" not in ban_data:
        return {"error": "Failed to retrieve ban status"}

    is_banned = ban_data["data"].get("is_banned", 0)
    period = ban_data["data"].get("period", 0)

    if is_banned:
        ban_message = f"Banned for {period} months" if period > 0 else "Banned indefinitely"
    else:
        ban_message = "Not banned"

    return {
        "ban_status": ban_message,
        "ban_period": f"{period} months" if is_banned and period > 0 else None
    }


def get_player_info(target_id):
    cookies = {
        '_ga': 'GA1.1.2123120599.1674510784',
        '_fbp': 'fb.1.1674510785537.363500115',
        '_ga_7JZFJ14B0B': 'GS1.1.1674510784.1.1.1674510789.0.0.0',
        'source': 'mb',
        'region': 'MA',
        'language': 'ar',
        '_ga_TVZ1LG7BEB': 'GS1.1.1674930050.3.1.1674930171.0.0.0',
        'datadome': '6h5F5cx_GpbuNtAkftMpDjsbLcL3op_5W5Z-npxeT_qcEe_7pvil2EuJ6l~JlYDxEALeyvKTz3~LyC1opQgdP~7~UDJ0jYcP5p20IQlT3aBEIKDYLH~cqdfXnnR6FAL0',
        'session_key': 'efwfzwesi9ui8drux4pmqix4cosane0y',
    }

    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Origin': 'https://shop2game.com',
        'Referer': 'https://shop2game.com/app/100067/idlogin',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Redmi Note 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
        'accept': 'application/json',
        'content-type': 'application/json',
        'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'x-datadome-clientid': '6h5F5cx_GpbuNtAkftMpDjsbLcL3op_5W5Z-npxeT_qcEe_7pvil2EuJ6l~JlYDxEALeyvKTz3~LyC1opQgdP~7~UDJ0jYcP5p20IQlT3aBEIKDYLH~cqdfXnnR6FAL0',
    }

    json_data = {
        'app_id': 100067,
        'login_id': target_id,
        'app_server_id': 0,
    }

    try:
        res = requests.post('https://shop2game.com/api/auth/player_id_login',
                            cookies=cookies, headers=headers, json=json_data,
                            timeout=REQUEST_TIMEOUT)
        if res.status_code != 200:
            return {
                "nickname": None,
                "region": None,
                "warning": f"Player info API returned HTTP {res.status_code}"
            }

        player_data = res.json()
        return {
            "nickname": player_data.get('nickname'),
            "region": player_data.get('region'),
        }
    except requests.exceptions.RequestException as e:
        return {
            "nickname": None,
            "region": None,
            "warning": f"Player info API request failed: {e}"
        }
    except ValueError:
        return {
            "nickname": None,
            "region": None,
            "warning": "Player info API returned invalid JSON"
        }


def check_player_info(target_id):
    ban_info = check_ban_info(target_id)
    if "error" in ban_info:
        return ban_info

    player_info = get_player_info(target_id)
    result = {
        "uid": target_id,
        "nickname": player_info.get("nickname"),
        "region": player_info.get("region"),
        **ban_info
    }

    if player_info.get("warning"):
        result["player_info_warning"] = player_info["warning"]

    return result

@app.route('/bancheck', methods=['GET'])
def check_ban_status():
    uid = request.args.get('uid')
    if not uid:
        return jsonify({"error": "UID parameter is required"}), 400
    if not uid.isdigit():
        return jsonify({"error": "UID must contain only numbers"}), 400

    result = check_player_info(uid)
    if "error" in result:
        return jsonify(result), 502

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
