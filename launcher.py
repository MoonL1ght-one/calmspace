# -*- coding: utf-8 -*-
"""
平静空间 launcher
------------------------------------------------
1. 在本机起一个只绑定 127.0.0.1 的小服务，把 index.html 发出去
2. 用 Edge / Chrome 的 kiosk 模式打开：真·全屏、无边框、无地址栏
3. 页面上输入「离开」后，页面请求 /__exit__，这里强制结束浏览器进程
   -> 窗口消失，回到正常桌面

不联网、不上传任何内容；所有内容只留在内存里。
"""

import ctypes
import http.server
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = "index.html"
EXIT = threading.Event()
TITLE = "平静空间"


def msgbox(text, icon=0x40):
    """icon: 0x40 信息 / 0x30 警告 / 0x10 错误"""
    try:
        ctypes.windll.user32.MessageBoxW(None, text, TITLE, icon)
    except Exception:
        pass


def log(text):
    try:
        with open(os.path.join(HERE, "error.log"), "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S  ") + text + "\n")
    except Exception:
        pass


# ------------------------------------------------------------------ 服务端
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=HERE, **kw)

    def log_message(self, *a):
        pass

    def _plain(self, body):
        data = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.startswith("/__exit__"):
            EXIT.set()
            self._plain("bye")
            return
        if self.path.startswith("/__ping__"):
            self._plain("ok")
            return
        super().do_GET()


class Server(http.server.ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def free_port():
    env = os.environ.get("CALM_PORT")
    if env:
        try:
            return int(env)
        except ValueError:
            pass
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


# ------------------------------------------------------------------ 浏览器
def find_browser():
    pf = os.environ.get("ProgramFiles", r"C:\Program Files")
    pf86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    local = os.environ.get("LOCALAPPDATA", "")
    cands = [
        os.path.join(pf86, r"Microsoft\Edge\Application\msedge.exe"),
        os.path.join(pf, r"Microsoft\Edge\Application\msedge.exe"),
        os.path.join(pf, r"Google\Chrome\Application\chrome.exe"),
        os.path.join(pf86, r"Google\Chrome\Application\chrome.exe"),
        os.path.join(local, r"Google\Chrome\Application\chrome.exe"),
        os.path.join(pf, r"BraveSoftware\Brave-Browser\Application\brave.exe"),
    ]
    for c in cands:
        if c and os.path.isfile(c):
            return c
    for name in ("msedge", "chrome", "brave"):
        p = shutil.which(name)
        if p:
            return p
    return None


def profile_dir():
    """每次运行都用全新的临时配置目录：
    既不会和用户自己的浏览器会话互相干扰，也不会出现「配置被占用」导致窗口无法关闭。"""
    d = os.path.join(tempfile.gettempdir(), "CalmSpace-%d-%d" % (os.getpid(), int(time.time())))
    try:
        os.makedirs(d, exist_ok=True)
        return d
    except Exception:
        d = os.path.join(tempfile.gettempdir(), "CalmSpace-profile")
        os.makedirs(d, exist_ok=True)
        return d


def drop_profile(path):
    for _ in range(4):
        try:
            shutil.rmtree(path, ignore_errors=False)
            return
        except Exception:
            time.sleep(0.4)


def launch_browser(exe, url):
    args = [
        exe,
        "--user-data-dir=" + profile_dir(),
        "--app=" + url,
        "--kiosk",
        "--start-fullscreen",
        "--no-first-run",
        "--no-default-browser-check",
        "--noerrdialogs",
        "--no-service-autorun",
        "--disable-breakpad",
        "--disable-sync",
        "--disable-extensions",
        "--disable-default-apps",
        "--disable-component-update",
        "--disable-background-networking",
        "--disable-session-crashed-bubble",
        "--hide-crash-restore-bubble",
        "--overscroll-history-navigation=0",
        "--disable-pinch",
        "--force-color-profile=srgb",
        "--disable-features=Translate,MediaRouter,OptimizationHints",
        "--autoplay-policy=no-user-gesture-required",
    ]
    return subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL), args[1].split("=", 1)[1]


def kill_tree(pid):
    try:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       creationflags=0x08000000, timeout=15)
    except Exception as e:
        log("taskkill failed: %r" % (e,))
        try:
            os.kill(pid, 9)
        except Exception:
            pass


# ------------------------------------------------------------------ 主流程
def main():
    if not os.path.isfile(os.path.join(HERE, PAGE)):
        msgbox("没有找到 %s，请把它和 launcher.py 放在同一个文件夹里。" % PAGE, 0x10)
        return

    port = free_port()
    url = "http://127.0.0.1:%d/%s?kiosk=1" % (port, PAGE)

    try:
        httpd = Server(("127.0.0.1", port), Handler)
    except Exception as e:
        log("server start failed: %r" % (e,))
        msgbox("小服务启动失败：%s" % e, 0x10)
        return

    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    proc = None
    prof = None
    serve_only = os.environ.get("CALM_NO_BROWSER") == "1"   # 自检用：只起服务
    if not serve_only:
        exe = find_browser()
        if exe:
            try:
                res = launch_browser(exe, url)
                if isinstance(res, tuple):
                    proc, prof = res
                else:
                    proc = res
            except Exception as e:
                log("browser launch failed: %r" % (e,))
        else:
            log("no browser found")
            msgbox("没有找到 Edge 或 Chrome，将用默认浏览器打开（不会是无边框全屏）。\n"
                   "建议安装 Microsoft Edge 后重试。", 0x30)

        if proc is None:
            # 兜底：默认浏览器打开（Html 页面自身会请求全屏）
            try:
                webbrowser.open(os.path.join(HERE, PAGE))
            except Exception as e:
                log("webbrowser.open failed: %r" % (e,))
                msgbox("打不开页面，请手动打开 %s" % PAGE, 0x10)
                httpd.shutdown()
                return

    # 等待：页面请求退出 / 浏览器被关掉 / 启动失败
    launched_at = time.time()
    immediate_fail = False
    while True:
        if EXIT.wait(0.35):
            break
        if proc is not None and proc.poll() is not None:
            if time.time() - launched_at < 3.0:
                immediate_fail = True
                log("browser process exited right after launch")
            break

    if proc is not None and proc.poll() is None:
        time.sleep(0.4)          # 让页面淡出动画收个尾
        kill_tree(proc.pid)

    try:
        httpd.shutdown()
        httpd.server_close()
    except Exception:
        pass

    if prof:
        drop_profile(prof)

    if immediate_fail:
        msgbox("浏览器没能正常启动。\n可以手动双击 index.html —— 会全屏打开，只是没有无边框效果。\n"
               "详细原因见同目录 error.log。", 0x30)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log("fatal: %r" % (e,))
        msgbox("出错了，详情见同目录 error.log：\n%r" % (e,), 0x10)
        sys.exit(1)
