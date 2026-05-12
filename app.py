from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

def check_player_info(target_id):
    try:
        # Player info API
        res = requests.post(
            'https://shop2game.com/api/auth/player_id_login',
            json={
                'app_id': 100067,
                'login_id': target_id,
                'app_server_id': 0,
            },
            timeout=10
        )

        if res.status_code != 200 or not res.json().get('nickname'):
            return {"error": "ID NOT FOUND"}

        player_data = res.json()
        nickname = player_data.get('nickname', 'N/A')
        region = player_data.get('region', 'N/A')

        # Ban check API
        ban_url = f'https://ff.garena.com/api/antihack/check_banned?lang=en&uid={target_id}'
        ban_res = requests.get(ban_url, timeout=10)
        ban_data = ban_res.json()

        if ban_data.get("status") == "success":
            data = ban_data.get("data", {})
            is_banned = data.get("is_banned", 0)
            period = data.get("period", 0)

            if is_banned:
                ban_message = f"Banned for {period} months" if period > 0 else "Banned indefinitely"
            else:
                ban_message = "Not banned"
        else:
            return {"error": "Ban API failed"}

        return {
            "uid": target_id,
            "nickname": nickname,
            "region": region,
            "ban_status": ban_message,
            "developed by": "pankaj-ux"
        }
,
    except Exception as e:
        return {"error": str(e)}


# ✅ HOME ROUTE (IMPORTANT)
@app.route('/')
def home():
    return jsonify({
        "status": "API is running",
        "endpoint": "/bancheck?uid=YOUR_UID",
        "developed by": "pankaj-ux"
    })


# End Point
@app.route('/bancheck', methods=['GET'])
def check_ban_status():
    uid = request.args.get('uid')

    if not uid:
        return jsonify({"error": "UID parameter is required"}), 400

    result = check_player_info(uid)

    if "error" in result:
        return jsonify(result), 404

    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
