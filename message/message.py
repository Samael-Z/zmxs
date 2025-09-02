import json
from Crypto.Cipher import AES
from google.protobuf.json_format import MessageToDict
from data import proto_pb2, base_pb2
from byte_buf import ByteBuffer

class NetMsgParser:
    def __init__(self):
        # 初始化密钥和消息映射表
        self._key = b'spqh4hpstria0q9h'
        self._msg_map = self._load_msg_map()
        self._buf_send = ByteBuffer()
        self._buf_recv = ByteBuffer()

    def feed(self, ts, direction, raw_bytes):
        # 按方向写入缓冲区
        buf = self._buf_recv if direction == 'recv' else self._buf_send
        buf.write_bytes(raw_bytes)
        return self._parse(ts, direction, buf)

    def _parse(self, ts, direction, buf):
        # 尝试从缓冲区解析完整消息
        out = []
        while True:
            if direction == 'send' and buf.readable_bytes() >= 2:
                msg_len = buf.peek_uint16()
            elif direction == 'recv' and buf.readable_bytes() >= 4:
                msg_len = buf.peek_uint32()
            else:
                break
            if buf.readable_bytes() < msg_len:
                break
            msg_bytes = buf.read_bytes(msg_len)
            parsed = self._parse_one(direction, msg_bytes)
            parsed.insert(0, ts)
            out.append(parsed)
        return out

    def _parse_one(self, direction, msg_bytes):
        # 解析单条消息
        buf = ByteBuffer(msg_bytes)
        if direction == 'send':
            _ = buf.read_uint16()
            msg_id = buf.read_uint16()
        elif direction == 'recv':
            _ = buf.read_uint32()
            msg_id = buf.read_uint16()
        else:
            raise Exception('方向错误: ' + str(direction))
        content = buf.read_bytes(buf.readable_bytes())
        # 仅对发送方向解密
        if direction == 'send' and content:
            content = self._aes_decrypt(content)
        # 查找消息定义
        info = self._msg_map.get(msg_id, None)
        if not info:
            return [direction, msg_id, 'UNKNOWN', {}, msg_bytes]
        name = info['name']
        proto = info['proto']
        # 解析protobuf
        if not proto:
            pb = {}
        else:
            pb = self._decode_proto(proto, content)
        return [direction, msg_id, name, pb, msg_bytes]

    def _aes_decrypt(self, data):
        # AES-ECB解密
        cipher = AES.new(self._key, AES.MODE_ECB)
        return self._unpad(cipher.decrypt(data))

    @staticmethod
    def _unpad(data):
        # PKCS#7去填充
        return data[:-data[-1]]

    def _decode_proto(self, proto_name, data):
        # 动态选择proto模块
        if proto_name.startswith('com.yofijoy.core.proto.'):
            mod = proto_pb2
        elif proto_name.startswith('base.'):
            mod = base_pb2
        else:
            return {}
        cls_name = proto_name.split('.')[-1]
        pb_obj = getattr(mod, cls_name)()
        pb_obj.ParseFromString(data)
        return MessageToDict(pb_obj)

    @staticmethod
    def _load_msg_map():
        # 加载消息ID映射表
        with open('data/protocol.json', 'r', encoding='utf-8') as f:
            proto = json.load(f)
        result = {}
        for cmd in proto.values():
            for typ in ('CCmd', 'SCmd'):
                if typ in cmd:
                    msg = cmd[typ]
                    name = msg['msgName']
                    mid = int(msg['msgId'])
                    proto_name = msg.get('protoName')
                    if proto_name == 'false':
                        proto_name = None
                    result[mid] = {'name': name, 'proto': proto_name}
        # 兼容补充ID
        for n, mid in getattr(proto_pb2, 'CSProtoId', {}).items():
            result.setdefault(mid, {'name': n, 'proto': None})
        return result

