import sys
import threading
import time
import argparse
import uvicorn
import webview
from server.app import app

def run_server(port: int):
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")

def main():
    parser = argparse.ArgumentParser(description="文档智能系统")
    parser.add_argument("--web", action="store_true", help="以纯 Web 模式启动（不打开本地桌面窗口）")
    parser.add_argument("--port", type=int, default=8199, help="服务端口")
    parser.add_argument("--debug", action="store_true", help="开启 Debug 模式（允许 F12 开发者工具）")
    args = parser.parse_args()

    port = args.port

    # Start FastAPI in a daemon thread
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()

    # Give server a moment to start
    time.sleep(1)

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
        # Desktop Window Mode
        window = webview.create_window(
            "文档智能系统 - 本地端", 
            url,
            width=1280, 
            height=800,
            min_size=(1024, 600),
        )
        webview.start(debug='--debug' in sys.argv)

if __name__ == '__main__':
    main()
