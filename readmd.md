# 项目说明（readmd.md）

## 项目简介
ZMXS手游的协议分析，代码比较乱，没有优化过，大体看看

## 目录结构
- `hook/`         —— 运行时脚本拦截与数据导出（如 Lua 脚本dump）
- `message/`      —— 协议消息解析与处理（如 protobuf 消息解析）
- `protobuf/`     —— 协议相关工具（Proto生成、协议映射、资源包处理等）
    - `main.py`              —— 主入口，自动生成协议文件和映射
    - `proto_generator.py`   —— 解析中间数据并生成proto文件
    - `protocol_mapping.py`  —— 生成协议ID与名称映射表
    - `script.py`            —— 资源包脚本提取与解密

## 依赖环境
- Python 3.8+
- 依赖库：
    - `protobuf`（Google Protocol Buffers）
    - `Crypto`（pycryptodome）
    - `UnityPy`（资源包处理）
- Frida（如需运行 hook/lua.ts 脚本）

## 快速上手
1. 安装依赖：
   ```bash
   pip install protobuf pycryptodome UnityPy
   ```
2. 运行协议生成与映射：
   ```bash
   cd protobuf
   python main.py
   ```
3. 资源包脚本提取：
   ```bash
   python script.py
   ```
4. 如需运行 hook/lua.ts，请在 Frida 环境下加载。
