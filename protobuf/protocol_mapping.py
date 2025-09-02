import json
import re
from pathlib import Path

def make_map():
    # 构建协议映射并输出
    proto_map = {}
    proto_map = _parse_cmds(proto_map)
    _fill_ids(proto_map)
    _fill_protos(proto_map)
    out = Path('data_bin/protocol.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', encoding='utf-8') as f:
        json.dump(proto_map, f, indent=4, ensure_ascii=False)

def _parse_cmds(proto_map):
    # 解析命令定义
    client = _parse_file(Path('data_src/cmd/CCmd.lua'))
    server = _parse_file(Path('data_src/cmd/SCmd.lua'))
    typemap = {c: 'CCmd' for c in client} | {s: 'SCmd' for s in server}
    for tup in [*client, *server]:
        typ = typemap[tup]
        cmd, name, comment = tup
        proto_map.setdefault(cmd, {})
        if typ in proto_map[cmd] and proto_map[cmd][typ]['msgName'] != name:
            raise Exception(f'命令冲突: {cmd} in {typ}')
        proto_map[cmd][typ] = {'msgName': name, 'comment': comment}
    return proto_map

def _fill_ids(proto_map):
    # 从proto文件提取消息ID
    msg2cmd = {info['msgName']: (cmd, typ)
               for cmd, infos in proto_map.items()
               for typ, info in infos.items()}
    proto_path = Path('data_bin/com.yofijoy.core.proto.proto')
    content = proto_path.read_text(encoding='utf-8')
    m = re.search(r'enum\s+CSProtoId\s*{(.*?)}', content, re.DOTALL)
    if not m:
        return
    enum_body = m.group(1)
    for name, mid in re.findall(r'(\w+)\s*=\s*(\d+);', enum_body):
        if name in msg2cmd:
            cmd, typ = msg2cmd[name]
            proto_map[cmd][typ]['msgId'] = int(mid)

def _fill_protos(proto_map):
    # 从桥接文件提取proto名
    bridge = Path('data_src/cmd/ProtobufBridge.lua').read_text(encoding='utf-8')
    for typ, cmd, p1, p2 in re.findall(r'(C|S)Cmd\.(\w+)\]\s*=\s*(?:"([^"]+)"|(true|false))', bridge):
        proto = p1 if p1 else p2
        full_typ = f'{typ}Cmd'
        if cmd in proto_map and full_typ in proto_map[cmd]:
            proto_map[cmd][full_typ]['protoName'] = proto

def _parse_file(path):
    # 解析命令定义文件
    res = []
    pat = re.compile(r'Cmd\.(\w+)\s*=\s*enum\("([^"]+)"\)(.*?)$')
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith('--') or 'Cmd.' not in line or 'enum(' not in line:
                continue
            m = pat.search(line)
            if m:
                cmd, name = m.group(1), m.group(2)
                comment = line.split('--', 1)[1].strip() if '--' in line else ''
                res.append((cmd, name, comment))
    return res
