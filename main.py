import sys
import os

# 确保项目根目录在 sys.path 中
_project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

if sys.stdout is None or sys.stderr is None:
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

import threading
import time
import argparse

def run_server(port: int):
    import uvicorn
    from server.app import app
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")

def main():
    parser = argparse.ArgumentParser(description="文档智能系统")
    parser.add_argument("--web", action="store_true", help="以纯 Web 模式启动（不打开本地桌面窗口）")
    parser.add_argument("--port", type=int, default=8199, help="服务端口")
    parser.add_argument("--debug", action="store_true", help="开启 Debug 模式（允许 F12 开发者工具）")
    args = parser.parse_args()

    port = args.port

    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()

    url = f"http://127.0.0.1:{port}"

    if args.web:
        print(f"服务器已启动在 {url}")
        print("以 Web 模式运行中...")
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            pass
    else:
        import webview

        loading_html = """
        <html><body style="display:flex;align-items:center;justify-content:center;height:100vh;margin:0;font-family:sans-serif;background:#f7f8fa">
        <div style="text-align:center;color:#646a73"><h2>文档智能系统</h2><p>正在启动服务，请稍候...</p></div>
        </body></html>
        """

        window = webview.create_window(
            "文档智能系统 - 本地端",
            html=loading_html,
            width=1280,
            height=800,
            min_size=(1024, 600),
        )

        def _wait_and_load():
            import urllib.request
            for _ in range(60):
                time.sleep(1)
                try:
                    urllib.request.urlopen(url, timeout=2)
                    window.load_url(url)
                    return
                except Exception:
                    pass

        threading.Thread(target=_wait_and_load, daemon=True).start()
        webview.start(debug='--debug' in sys.argv)

if __name__ == '__main__':
    main()