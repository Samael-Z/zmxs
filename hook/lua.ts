// 入口函数，负责主逻辑挂钩
function startDump() {
    // 监听libulua.so的luaL_loadbufferx导出函数
    Interceptor.attach(Module.findExportByName('libulua.so', 'luaL_loadbufferx'), {
        onEnter(args) {
            // 获取脚本名和大小
            const scriptName = args[3].readUtf8String();
            const scriptSize = args[2].toInt32();
            const scriptPtr = args[1];
            // 只处理.lua结尾的脚本
            if (!scriptName.endsWith('.lua')) return;
            // 拼接输出路径
            const outPath = `/sdcard/dump/${scriptName}`;
            makeDirs(outPath); // 确保目录存在
            // 写入文件
            const file = new File(outPath, 'wb');
            file.write(scriptPtr.readByteArray(scriptSize));
            file.flush();
            file.close();
            // 输出日志
            console.log(`[DUMP] ${outPath} (${scriptSize} bytes)`);
        }
    });
}

// 低级mkdir函数，直接调用系统API
const sysMkdir = new NativeFunction(Module.findExportByName(null, 'mkdir'), 'int', ['pointer', 'int']);

// 递归创建目录，兼容多级路径
function makeDirs(fullPath) {
    // 去除末尾斜杠
    let cleanPath = fullPath.replace(/\/+$/, '');
    // 拆分路径
    let segs = cleanPath.split('/');
    if (segs.length < 2) return; // 路径太短不处理
    segs.pop(); // 去掉文件名
    let cur = '';
    // 逐级创建目录
    for (let seg of segs) {
        if (!seg) continue;
        cur += '/' + seg;
        sysMkdir(Memory.allocUtf8String(cur), 0x0FFF);
    }
}

// 标记是否已挂钩，防止重复
let alreadyHooked = false;
// 动态库加载时自动挂钩
Interceptor.attach(Module.findExportByName(null, 'android_dlopen_ext'), {
    onEnter(args) {
        this.libPath = args[0].readCString();
    },
    onLeave() {
        if (this.libPath && this.libPath.includes('libulua.so') && !alreadyHooked) {
            alreadyHooked = true;
            startDump();
        }
    }
});
// 可选：立即执行主逻辑（如需调试可打开）
// setImmediate(startDump);