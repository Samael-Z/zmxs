import os
import pathlib
import shutil
import UnityPy

# 资源包路径
ASSET_PATH = r"AssetBundles"
# 目标目录
BIN_DIR = "data_bin"

def dump_scripts(pkg_path, out_dir=BIN_DIR):
    # 加载资源包
    env = UnityPy.load(pkg_path)
    # 遍历所有对象
    for asset_path, obj in env.container.items():
        data = obj.read()
        # 生成输出路径
        dest = os.path.join(out_dir, *asset_path.split("/"))
        dest = dest.replace('.bytes', '')
        # 确保目录存在
        pathlib.Path(os.path.dirname(dest)).mkdir(parents=True, exist_ok=True)
        # 写入脚本内容
        with open(dest, 'wb') as f:
            f.write(data.m_Script.encode('utf-8'))
        print(f"[EXTRACTED] {dest}")

def xor_decrypt(data: bytearray, pwd: str):
    # 简单异或解密
    if not data or not pwd:
        return
    plen = len(pwd)
    for i in range(len(data)):
        data[i] ^= ord(pwd[i % plen])

def main():
    # 示例：解密并打印前32字节
    with open('test.assetpkg', 'rb') as f:
        buf = bytearray(f.read())
    # 如需批量提取脚本，取消注释
    # shutil.rmtree("data_bin/assets", ignore_errors=True)
    # dump_scripts(f"{BIN_DIR}/luagame.assetpkg")
    # dump_scripts(f"{BIN_DIR}/luastarter.assetpkg")

if __name__ == '__main__':
    main()
