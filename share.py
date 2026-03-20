import os
import subprocess
from pyngrok import ngrok
import time
import sys

def launch():
    print("🚀 Starting Solana Watcher Pro with Ngrok...")
    
    # 1. Start Streamlit in the background
    # We use sys.executable to ensure we use the same python environment
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"]
    process = subprocess.Popen(cmd)
    
    # 2. Wait a bit for streamlit to start
    time.sleep(3)
    
    # 3. Start Ngrok tunnel
    try:
        # Check if auth token is set in environment or config
        public_url = ngrok.connect(8501).public_url
        print(f"\n✅ Your app is now live at: {public_url}")
        print("🔗 Share this link with anyone!")
        print("\nPress Ctrl+C to stop both Streamlit and Ngrok.")
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        process.terminate()
        ngrok.kill()
    except Exception as e:
        print(f"❌ Error starting Ngrok: {e}")
        print("Note: Make sure you have set your NGROK_AUTHTOKEN if required.")
        process.terminate()

if __name__ == "__main__":
    launch()
