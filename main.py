import os
import sys
import time
import json
import random
import socket
import asyncio
import binascii
import re
import ssl
import urllib3
import aiohttp
import threading
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from cfonts import render
from flask import Flask, jsonify, request, render_template

from xC4 import *
from xHeaders import *

from Pb2 import DEcwHisPErMsG_pb2, MajoRLoGinrEs_pb2, PorTs_pb2, MajoRLoGinrEq_pb2, sQ_pb2, Team_msg_pb2
from game_version import CLIENT_VERSION, CLIENT_VERSION_CODE, UNITY_VERSION, RELEASE_VERSION, ANDROID_OS_VERSION, USER_AGENT_MODEL

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  

DEV_SIGNATURE = "[FF0000] Dev:[FFFFFF]—͟͞͞ </> Ɽɩɗʋαɳʋℓ ɨѕℓαɱ"

Hr = {
    'X-Unity-Version': UNITY_VERSION,
    'ReleaseVersion': RELEASE_VERSION,
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-GA': 'v1 1',
    'User-Agent': f"Dalvik/2.1.0 (Linux; U; {ANDROID_OS_VERSION}; {USER_AGENT_MODEL} Build/PI)",
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip'
}

app = Flask(__name__)
GLOBAL_BOTS = {} 
bot_loop = asyncio.new_event_loop()

class BotState:
    def __init__(self, uid, password, config_server_name="UNKNOWN"):
        self.login_uid = uid
        self.password = password
        self.config_server_name = config_server_name
        self.actual_bot_uid = None
        self.region = "sg"
        self.key = None
        self.iv = None
        self.online_writer = None
        self.whisper_writer = None

async def encrypted_proto(encoded_hex):
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(encoded_hex, AES.block_size))
    
async def GeNeRaTeAccEss(uid, password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {"Host": "100067.connect.garena.com", "User-Agent": f"Dalvik/2.1.0 (Linux; U; {ANDROID_OS_VERSION}; {USER_AGENT_MODEL} Build/PI)", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"uid": uid, "password": password, "response_type": "token", "client_type": "2", "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3", "client_id": "100067"}
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    try:
        connector = aiohttp.TCPConnector(ssl=ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(url, headers=headers, data=data, timeout=15) as response:
                if response.status != 200: return None, None
                d = await response.json()
                return d.get("open_id"), d.get("access_token")
    except: return None, None

async def EncRypTMajoRLoGin(open_id, access_token):
    major_login = MajoRLoGinrEq_pb2.MajorLogin()
    major_login.event_time = str(datetime.now())[:-7]
    major_login.game_name = "free fire"
    major_login.platform_id = 1
    major_login.client_version = CLIENT_VERSION
    major_login.system_software = f"{ANDROID_OS_VERSION} / API-28"
    major_login.system_hardware = "Handheld"
    major_login.telecom_operator = "Verizon"
    major_login.network_type = "WIFI"
    major_login.screen_width = 1920
    major_login.screen_height = 1080
    major_login.screen_dpi = "280"
    major_login.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
    major_login.memory = 3003
    major_login.gpu_renderer = "Adreno (TM) 640"
    major_login.gpu_version = "OpenGL ES 3.1 v1.46"
    major_login.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    major_login.client_ip = "223.191.51.89"
    major_login.language = "en"
    major_login.open_id = open_id
    major_login.open_id_type = "4"
    major_login.device_type = "Handheld"
    major_login.access_token = access_token
    major_login.platform_sdk_id = 1
    major_login.network_operator_a = "Verizon"
    major_login.network_type_a = "WIFI"
    major_login.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    major_login.login_by = 3
    major_login.library_path = "/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64"
    major_login.reg_avatar = 1
    major_login.channel_type = 3
    major_login.cpu_type = 2
    major_login.cpu_architecture = "64"
    major_login.client_version_code = CLIENT_VERSION_CODE
    major_login.graphics_api = "OpenGLES2"
    major_login.supported_astc_bitset = 16383
    major_login.login_open_id_type = 4
    major_login.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWA0FUgsvA1snWlBaO1kFYg=="
    major_login.loading_time = 13564
    major_login.release_channel = "android"
    major_login.origin_platform_type = "4"
    major_login.primary_platform_type = "4"
    return await encrypted_proto(major_login.SerializeToString())

async def MajorLogin(payload):
    url = "https://loginbp.ggblueshark.com/MajorLogin"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=Hr, ssl=ssl_context) as response:
            if response.status == 200: return await response.read()
            return None

async def GetLoginData(base_url, payload, token):
    url = f"{base_url}/GetLoginData"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    Hr['Authorization']= f"Bearer {token}"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=Hr, ssl=ssl_context) as response:
            if response.status == 200: return await response.read()
            return None

async def DecRypTMajoRLoGin(MajoRLoGinResPonsE):
    proto = MajoRLoGinrEs_pb2.MajorLoginRes()
    proto.ParseFromString(MajoRLoGinResPonsE)
    return proto

async def DecRypTLoGinDaTa(LoGinDaTa):
    proto = PorTs_pb2.GetLoginData()
    proto.ParseFromString(LoGinDaTa)
    return proto

async def DecodeWhisperMessage(hex_packet):
    packet = bytes.fromhex(hex_packet)
    proto = DEcwHisPErMsG_pb2.DecodeWhisper()
    proto.ParseFromString(packet)
    return proto
    
async def xAuThSTarTuP(TarGeT, token, timestamp, key, iv):
    uid_hex = hex(TarGeT)[2:]
    uid_length = len(uid_hex)
    encrypted_timestamp = await DecodE_HeX(timestamp)
    encrypted_account_token = token.encode().hex()
    encrypted_packet = await EnC_PacKeT(encrypted_account_token, key, iv)
    encrypted_packet_length = hex(len(encrypted_packet) // 2)[2:]
    headers = '0000000' if uid_length == 9 else '00000000' if uid_length == 8 else '000000' if uid_length == 10 else '000000000'
    return f"0115{headers}{uid_hex}{encrypted_timestamp}00000{encrypted_packet_length}{encrypted_packet}"

async def TcPOnLine(ip, port, AutHToKen, bot, reconnect_delay=0.5):
    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            bot.online_writer = writer
            writer.write(bytes.fromhex(AutHToKen))
            await writer.drain()
            while True:
                data2 = await reader.read(9999)
                if not data2: break
                
                d_hex = data2.hex()
                if d_hex.startswith('0500') and len(d_hex) > 1000:
                    try:
                        packet = json.loads(await DeCode_PackEt(d_hex[10:]))
                        OwNer_UiD, CHaT_CoDe, SQuAD_CoDe = await GeTSQDaTa(packet)
                        JoinCHaT = await AutH_Chat(3, OwNer_UiD, CHaT_CoDe, bot.key, bot.iv)
                        if bot.whisper_writer:
                            bot.whisper_writer.write(JoinCHaT)
                            await bot.whisper_writer.drain()
                    except: pass
            if bot.online_writer:
                bot.online_writer.close(); await bot.online_writer.wait_closed(); bot.online_writer = None
        except Exception as e: bot.online_writer = None
        await asyncio.sleep(reconnect_delay)
                            
async def TcPChaT(ip, port, AutHToKen, bot, reconnect_delay=0.5):
    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            bot.whisper_writer = writer
            writer.write(bytes.fromhex(AutHToKen))
            await writer.drain()
            while True:
                data = await reader.read(9999)
                if not data: break
            if bot.whisper_writer:
                bot.whisper_writer.close(); await bot.whisper_writer.wait_closed(); bot.whisper_writer = None
        except Exception as e: bot.whisper_writer = None
        await asyncio.sleep(reconnect_delay)

async def RunAccount(bot: BotState):
    login_attempts = 0
    max_attempts = 3
    while True:
        try:
            open_id, access_token = await GeNeRaTeAccEss(bot.login_uid, bot.password)
            if not open_id: 
                login_attempts += 1
                if login_attempts >= max_attempts:
                    print(f"[🚫 SKIPPED] Account {bot.login_uid} ({bot.config_server_name}) failed {max_attempts} times.")
                    return 
                print(f"[❌ ERROR] Login Failed {bot.login_uid}. Retrying...")
                await asyncio.sleep(5)
                continue
            
            PyL = await EncRypTMajoRLoGin(open_id, access_token)
            MajoRLoGinResPonsE = await MajorLogin(PyL)
            if not MajoRLoGinResPonsE:
                login_attempts += 1
                if login_attempts >= max_attempts: return
                await asyncio.sleep(5)
                continue
            
            login_attempts = 0 
            MajoRLoGinauTh = await DecRypTMajoRLoGin(MajoRLoGinResPonsE)
            bot.key = MajoRLoGinauTh.key
            bot.iv = MajoRLoGinauTh.iv
            bot.region = MajoRLoGinauTh.region
            bot.actual_bot_uid = str(MajoRLoGinauTh.account_uid)
            
            if bot.config_server_name not in GLOBAL_BOTS: GLOBAL_BOTS[bot.config_server_name] = []
            if bot not in GLOBAL_BOTS[bot.config_server_name]: GLOBAL_BOTS[bot.config_server_name].append(bot)

            LoGinDaTa = await GetLoginData(MajoRLoGinauTh.url, PyL, MajoRLoGinauTh.token)
            if not LoGinDaTa: continue
            DecodedLogin = await DecRypTLoGinDaTa(LoGinDaTa)
            
            if not DecodedLogin.Online_IP_Port or ":" not in DecodedLogin.Online_IP_Port: continue
            OnLineiP, OnLineporT = DecodedLogin.Online_IP_Port.split(":")
            ChaTiP, ChaTporT = DecodedLogin.AccountIP_Port.split(":")

            AutHToKen = await xAuThSTarTuP(int(bot.actual_bot_uid), MajoRLoGinauTh.token, int(MajoRLoGinauTh.timestamp), bot.key, bot.iv)
            
            print(f"[✅ SUCCESS] Category: {bot.config_server_name:<11} | Server: {bot.region.upper():<4} | Acc: {bot.login_uid:<10} | Name: {DecodedLogin.AccountName} | Status: ONLINE")
            
            task1 = asyncio.create_task(TcPChaT(ChaTiP, ChaTporT, AutHToKen, bot))
            task2 = asyncio.create_task(TcPOnLine(OnLineiP, OnLineporT, AutHToKen, bot))
            
            done, pending = await asyncio.wait([task1, task2], return_when=asyncio.FIRST_COMPLETED)
            for task in pending: task.cancel()
            
            if bot in GLOBAL_BOTS.get(bot.config_server_name, []):
                GLOBAL_BOTS[bot.config_server_name].remove(bot)

            await asyncio.sleep(3)
            
        except Exception as e: await asyncio.sleep(5)

async def RunAllBots(accounts_config):
    tasks = []
    for server_category, acc_list in accounts_config.items():
        if isinstance(acc_list, list):
            for acc in acc_list:
                if "uid" in acc and "password" in acc:
                    tasks.append(asyncio.create_task(RunAccount(BotState(acc["uid"], acc["password"], server_category))))
                    await asyncio.sleep(0.5) 
    if tasks: await asyncio.gather(*tasks)

def start_bot_thread(config):
    asyncio.set_event_loop(bot_loop)
    bot_loop.run_until_complete(RunAllBots(config))


# ----------------- FLASK & PWA DASHBOARD ROUTES -----------------
@app.route('/')
def home():
    return render_template('index.html')

# PWA Manifest Route
@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "Riduan Emote Pro",
        "short_name": "Emote Pro",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#05050a",
        "theme_color": "#3b82f6",
        "icons": [{
            "src": "https://i.ibb.co.com/QvxY46P2/1777527378786.png",
            "sizes": "512x512",
            "type": "image/png"
        }]
    })

# PWA Service Worker Route
@app.route('/sw.js')
def sw():
    sw_content = """
    self.addEventListener('install', (e) => { self.skipWaiting(); });
    self.addEventListener('activate', (e) => { e.waitUntil(clients.claim()); });
    self.addEventListener('fetch', (e) => { e.respondWith(fetch(e.request)); });
    """
    return app.response_class(sw_content, mimetype='application/javascript')

@app.route('/api/bots')
def get_active_bots():
    active_data = {}
    for server, bots in GLOBAL_BOTS.items():
        active_data[server] = [b.actual_bot_uid for b in bots if b.online_writer]
    return jsonify(active_data)

@app.route('/api/emotes')
def get_emotes():
    try:
        with open("emotes.json", "r") as f:
            return jsonify(json.load(f))
    except:
        return jsonify({"Error": "emotes.json not found"})

# --- EMOTE EXECUTION ---
async def execute_web_re(bot, team_code, target_uids, emote_id):
    try:
        join_pkt = await GenJoinSquadsPacket(team_code, bot.key, bot.iv)
        bot.online_writer.write(join_pkt)
        await bot.online_writer.drain()
        
        await asyncio.sleep(0.15) 
        
        combined_emotes = b""
        for t_uid in target_uids:
            if str(t_uid).isdigit():
                combined_emotes += await Emote_k(int(t_uid), int(emote_id), bot.key, bot.iv, bot.region)
                
        if combined_emotes:
            bot.online_writer.write(combined_emotes)
            await bot.online_writer.drain()
            
        await asyncio.sleep(0.05) 
        
        leave_pkt = await ExiT(None, bot.key, bot.iv)
        bot.online_writer.write(leave_pkt)
        await bot.online_writer.drain()
    except Exception as e: pass

@app.route('/api/trigger', methods=['POST'])
def trigger_emote():
    data = request.json
    server = data.get('server')
    bot_uid = data.get('bot_uid')
    team_code = data.get('team_code')
    target_uids = data.get('target_uids', [])
    emote_id = data.get('emote_id')
    
    target_bot = next((b for b in GLOBAL_BOTS.get(server, []) if b.actual_bot_uid == bot_uid and b.online_writer), None)
    if not target_bot: return jsonify({"error": "Selected bot is disconnected"}), 400
        
    asyncio.run_coroutine_threadsafe(execute_web_re(target_bot, team_code, target_uids, emote_id), bot_loop)
    return jsonify({"status": "success"})

# --- INVITE EXECUTION ---
async def execute_web_invite(bot, target_uid):
    try:
        bot.online_writer.write(await OpEnSq(bot.key, bot.iv, bot.region))
        await bot.online_writer.drain()
        await asyncio.sleep(0.3)
        
        bot.online_writer.write(await cHSq(5, int(target_uid), bot.key, bot.iv, bot.region))
        await bot.online_writer.drain()
        await asyncio.sleep(0.3)
        
        bot.online_writer.write(await SEnd_InV(5, int(target_uid), bot.key, bot.iv, bot.region))
        await bot.online_writer.drain()
        
        await asyncio.sleep(3.0)
        
        bot.online_writer.write(await ExiT(None, bot.key, bot.iv))
        await bot.online_writer.drain()
    except Exception as e: pass

@app.route('/api/invite', methods=['POST'])
def trigger_invite():
    data = request.json
    server = data.get('server')
    bot_uid = data.get('bot_uid')
    target_uid = data.get('target_uid')
    
    target_bot = next((b for b in GLOBAL_BOTS.get(server, []) if b.actual_bot_uid == bot_uid and b.online_writer), None)
    if not target_bot: return jsonify({"error": "Selected bot is disconnected"}), 400
        
    asyncio.run_coroutine_threadsafe(execute_web_invite(target_bot, target_uid), bot_loop)
    return jsonify({"status": "success"})

# --- ADMIN PANEL LOGIC ---
@app.route('/api/admin/upload', methods=['POST'])
def admin_upload():
    data = request.json
    if data.get('username') != 'riduan03' or data.get('password') != 'riduan03':
        return jsonify({"error": "Invalid Admin Credentials!"}), 401
    
    category = data.get('category')
    raw_ids = data.get('emotes', [])
    
    try:
        with open("emotes.json", "r") as f: emotes_data = json.load(f)
    except:
        emotes_data = {"Evo Emotes": [], "Rare Emotes": [], "Old Emotes": [], "All Emotes": []}
        
    if category not in emotes_data: emotes_data[category] = []
    if "All Emotes" not in emotes_data: emotes_data["All Emotes"] = []
        
    existing_cat = set(emotes_data[category])
    existing_all = set(emotes_data["All Emotes"])
    
    added = 0
    for eid in raw_ids:
        try:
            eid_int = int(eid)
            if eid_int not in existing_cat:
                emotes_data[category].append(eid_int)
                existing_cat.add(eid_int)
                added += 1
            if eid_int not in existing_all:
                emotes_data["All Emotes"].append(eid_int)
                existing_all.add(eid_int)
        except: pass
        
    with open("emotes.json", "w") as f:
        json.dump(emotes_data, f, indent=2)
        
    return jsonify({"status": "success", "added": added})

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == '__main__':
    os.system('clear')
    try: print(render('Riduan', colors=['white', 'green'], align='center'))
    except: pass
    
    print("\n💡 Architecture: Ultimate PWA Web Controller & Smart Multi-Bot")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    try:
        with open("bot_config.json", "r") as f:
            config = json.load(f)
            
        threading.Thread(target=start_bot_thread, args=(config,), daemon=True).start()
        
        local_ip = get_local_ip()
        print(f"🔥 WEB DASHBOARD IS READY!")
        print(f"👉 Local Access (Same Device): http://127.0.0.1:5000")
        print(f"👉 LAN Access (Other Devices): http://{local_ip}:5000\n")
        
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
            
    except Exception as e:
        print(f"❌ Initialization Error: {e}")
