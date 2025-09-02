import json
import os
import subprocess
from pathlib import Path

def make_proto():
    # 步骤1：用Lua脚本生成中间JSON
    _run_lua()
    # 步骤2：读取JSON
    with open('data_src/proto/CSProto.json', encoding='utf-8') as f:
        cs = json.load(f)
    # 步骤3：按包分组
    pkgs = _group(cs)
    # 步骤4：生成proto文件
    for pkg, msgs in pkgs.items():
        _write(pkg, msgs)
    # 步骤5：编译proto
    _compile()
    # 步骤6：清理临时文件
    _clean([
        Path('data_src/proto/CSProto.json'),
        Path('data_src/proto/base.json')
    ])

def _run_lua():
    # 调用Lua脚本生成JSON
    subprocess.run([
        'lua', 'pb_parser.lua'
    ], cwd=Path('data_src/proto'), capture_output=True, text=True, check=True)

def _group(cs):
    # 按包名分组
    pkgs = {}
    for msg in cs.values():
        msg['name'] = msg['name'][1:]
        pkg = msg['name'].removesuffix(f'.{msg["basename"]}')
        if pkg.startswith('google'):
            continue
        pkgs.setdefault(pkg, {})[msg['name']] = msg
    return pkgs

def _write(pkg, msgs):
    # 写proto文件
    lines = _build(pkg, msgs)
    out = Path('data_bin') / f'{pkg}.proto'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines), encoding='utf-8')

def _build(pkg, msgs):
    # 构造proto内容
    lines = [
        'syntax = "proto3";',
        f'package {pkg};',
    ]
    if pkg != 'base':
        lines.append('import "base.proto";')
    lines.append('')
    for m in msgs.values():
        lines.extend(_msg_or_enum(m, pkg))
        lines.append('')
    return lines

def _msg_or_enum(m, pkg):
    # 生成message或enum定义
    lines = [f"{m['type']} {m['basename']} {{"]
    fields = m['fields']
    if isinstance(fields, dict):
        for k in sorted(fields):
            f = fields[k]
            t = f['type'].replace(f'.{pkg}.', '').replace('.base.', 'base.')
            if m['type'] == 'message':
                lines.append(f"    {t} {f['name']} = {f['number']};")
            elif m['type'] == 'enum':
                lines.append(f"    {f['name']} = {f['number']};")
    lines.append('}')
    return lines

def _compile():
    # 编译所有proto为Python
    outdir = Path('data_bin/python')
    outdir.mkdir(parents=True, exist_ok=True)
    cmd = [
        '..\\data_src\\proto\\protoc.exe',
        '--proto_path=.',
        '--python_out=./python',
        '*.proto'
    ]
    subprocess.run(cmd, cwd=Path('data_bin'), shell=True, check=True)

def _clean(files):
    # 删除临时文件
    for f in files:
        if f.exists():
            f.unlink()
