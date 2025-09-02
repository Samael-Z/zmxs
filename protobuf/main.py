import os
import shutil
import proto_generator as pg
import protocol_mapping as pm

def run():
    # 清理目标目录并重建
    reset_bin_dir()
    # 生成proto文件并编译
    pg.make_proto()
    # 生成协议映射
    pm.make_map()

def reset_bin_dir():
    # 直接删再建，简单粗暴
    shutil.rmtree('data_bin', ignore_errors=True)
    os.makedirs('data_bin', exist_ok=True)

if __name__ == '__main__':
    run()
