import json, asyncio, random, urllib3
from protobuf_decoder.protobuf_decoder import Parser
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from game_version import CLIENT_VERSION

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

Key, Iv = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56]), bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

async def EnC_PacKeT(HeX, K, V): 
    return AES.new(K, AES.MODE_CBC, V).encrypt(pad(bytes.fromhex(HeX), 16)).hex()

async def EnC_Uid(H, Tp):
    e, H = [], int(H)
    while H:
        e.append((H & 0x7F) | (0x80 if H > 0x7F else 0)); H >>= 7
    return bytes(e).hex() if Tp == 'Uid' else None

async def EnC_Vr(N):
    if N < 0: return b''
    H = []
    while True:
        BesTo = N & 0x7F; N >>= 7
        if N: BesTo |= 0x80
        H.append(BesTo)
        if not N: break
    return bytes(H)

async def CrEaTe_VarianT(field_number, value):
    return await EnC_Vr((field_number << 3) | 0) + await EnC_Vr(value)

async def CrEaTe_LenGTh(field_number, value):
    encoded_value = value.encode() if isinstance(value, str) else value
    return await EnC_Vr((field_number << 3) | 2) + await EnC_Vr(len(encoded_value)) + encoded_value

async def CrEaTe_ProTo(fields):
    packet = bytearray()
    for field, value in fields.items():
        if isinstance(value, dict):
            nested_packet = await CrEaTe_ProTo(value)
            packet.extend(await CrEaTe_LenGTh(field, nested_packet))
        elif isinstance(value, int):
            packet.extend(await CrEaTe_VarianT(field, value))
        elif isinstance(value, str) or isinstance(value, bytes):
            packet.extend(await CrEaTe_LenGTh(field, value))
    return packet
    
async def DecodE_HeX(H):
    F = str(hex(H))[2:]
    return "0" + F if len(F) == 1 else F

async def Fix_PackEt(parsed_results):
    result_dict = {}
    for result in parsed_results:
        field_data = {'wire_type': result.wire_type}
        if result.wire_type in ["varint", "string", "bytes"]:
            field_data['data'] = result.data
        elif result.wire_type == 'length_delimited':
            field_data["data"] = await Fix_PackEt(result.data.results)
        result_dict[result.field] = field_data
    return result_dict

async def DeCode_PackEt(input_text):
    try:
        return json.dumps(await Fix_PackEt(Parser().parse(input_text)))
    except: return None
                      
def xMsGFixinG(uid):
    uid_str = str(uid)
    return ''.join('[C]' + uid_str[i:i+3] for i in range(0, len(uid_str), 3))

async def get_random_avatar():
    return random.choice([902042010, 902049003])

async def xSEndMsg(Msg, Tp, Tp2, id, K, V, region="BD"):
    fields = {
        1: id, 2: Tp2, 3: Tp, 4: Msg, 5: 1735129800, 7: 2, 
        9: {
            1: "xBesTo - C4", 2: int(await get_random_avatar()), 3: 901027027, 4: 330, 
            5: 801046529, 8: "xBesTo - C4", 10: 1, 11: 1, 13: {1: 2}, 
            14: {1: 12484827014, 2: 8, 3: b"\x10\x15\x08\n\x0b\x13\x0c\x0f\x11\x04\x07\x02\x03\x0d\x0e\x12\x01\x05\x06"}, 12: 0
        }, 10: "en", 13: {3: 1},
        14: {1: {1: 3, 2: 7, 3: 170, 4: 1, 5: 1740196800, 6: region}}
    }
    Pk = (await CrEaTe_ProTo(fields)).hex()
    return await GeneRaTePk("080112" + await EnC_Uid(len(Pk) // 2, Tp='Uid') + Pk, '1201', K, V)

async def GenJoinSquadsPacket(code, K, V):
    fields = {
        1: 4,
        2: {
            4: bytes.fromhex("01090a0b121920"), 5: str(code), 6: 6, 8: 1,
            9: {2: 800, 6: 11, 8: CLIENT_VERSION, 9: 5, 10: 1}
        }
    }
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)   

async def Emote_k(TarGeT, idT, K, V, region):
    fields = {1: 21, 2: {1: 804266360, 2: 909000001, 5: {1: TarGeT, 3: idT}}}
    packet = '0514' if region.lower() == "ind" else "0519" if region.lower() == "bd" else "0515"
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), packet, K, V)

async def GeTSQDaTa(D):
    return D['5']['data']['1']['data'], D["5"]["data"]["17"]["data"], D["5"]["data"]["31"]["data"]

async def AutH_Chat(T, uid, code, K, V):
    fields = {1: T, 2: {1: uid, 3: "en", 4: str(code)}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '1215', K, V)

async def GeneRaTePk(Pk, N, K, V):
    PkEnc = await EnC_PacKeT(Pk, K, V)
    _ = await DecodE_HeX(int(len(PkEnc) // 2))
    HeadEr = N + "000000" if len(_) == 2 else N + "00000" if len(_) == 3 else N + "0000" if len(_) == 4 else N + "000" if len(_) == 5 else ""
    return bytes.fromhex(HeadEr + _ + PkEnc)

async def OpEnSq(K, V, region):
    fields = {1: 1, 2: {2: "\u0001", 3: 1, 4: 1, 5: "en", 9: 1, 11: 1, 13: 1, 14: {2: 5756, 6: 11, 8: CLIENT_VERSION, 9: 2, 10: 4}}}
    packet = '0514' if region.lower() == "ind" else "0519" if region.lower() == "bd" else "0515"
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), packet, K, V)

async def cHSq(Nu, Uid, K, V, region):
    fields = {1: 17, 2: {1: int(Uid), 2: 1, 3: int(Nu - 1), 4: 62, 5: "\u001a", 8: 5, 13: 329}}
    packet = '0514' if region.lower() == "ind" else "0519" if region.lower() == "bd" else "0515"
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), packet, K, V)

async def SEnd_InV(Nu, Uid, K, V, region):
    fields = {1: 2, 2: {1: int(Uid), 2: region, 4: int(Nu)}}
    packet = '0514' if region.lower() == "ind" else "0519" if region.lower() == "bd" else "0515"
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), packet, K, V)
    
async def ExiT(idT, K, V):
    fields = {1: 7, 2: {1: idT} if idT else {}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)
