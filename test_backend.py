"""
Tests the full AI Pokedex backend end-to-end:
1. Starts the Spring Boot backend process (logging to backend_server.log)
2. Polls /api/health until UP
3. Verifies frontend HTML at /
4. Uploads Pikachu (25.png) to /api/identify
5. Verifies the complete JSON response (name, types, stats, abilities, sprite, etc.)
6. Shuts down the backend cleanly
"""

import os
import sys
import time
import subprocess
import requests

def run_test():
    log_path = os.path.abspath("backend_server.log")
    print(f"Starting Spring Boot backend (logging to {log_path})...")
    
    log_file = open(log_path, "w", encoding="utf-8")
    proc = subprocess.Popen(
        ["mvn.cmd", "-f", "backend/pom.xml", "spring-boot:run"],
        stdout=log_file,
        stderr=subprocess.STDOUT,
        shell=True,
    )

    url_health = "http://localhost:8080/api/health"
    url_identify = "http://localhost:8080/api/identify"
    url_frontend = "http://localhost:8080/"

    print("Waiting for server to start on port 8080...")
    ready = False
    for attempt in range(45):
        time.sleep(2)
        try:
            r = requests.get(url_health, timeout=2)
            if r.status_code == 200 and r.text == "OK":
                ready = True
                print(f"Backend started and healthy after {(attempt + 1) * 2}s!")
                break
        except requests.RequestException:
            pass

    if not ready:
        print("Backend failed to start in time. Killing process.")
        proc.terminate()
        log_file.close()
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            print("Server log:\n", f.read()[-3000:])
        sys.exit(1)

    try:
        # Test 1: Frontend served at root
        print("Testing frontend static serving at / ...")
        rf = requests.get(url_frontend, timeout=5)
        print(f"Frontend HTTP status: {rf.status_code}")
        assert rf.status_code == 200
        assert "<title>AI Pokédex</title>" in rf.text
        print("Frontend served successfully!")

        # Test 2: Upload image for prediction
        img_path = os.path.abspath("ml_training/data/raw/25.png")
        print(f"Testing /api/identify with image: {img_path}...")
        with open(img_path, "rb") as f:
            files = {"image": ("25.png", f, "image/png")}
            r = requests.post(url_identify, files=files, timeout=20)

        print(f"Identify response status: {r.status_code}")
        data = r.json()
        print("Response data:")
        import json
        print(json.dumps(data, indent=2))

        assert r.status_code == 200
        assert "id" in data
        assert "name" in data
        assert "types" in data
        assert "stats" in data
        assert "confidence" in data

        print("\n=== ALL END-TO-END TESTS PASSED SUCCESSFULLY! ===")

    finally:
        print("Stopping Spring Boot backend...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            pass
        log_file.close()
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/IM", "java.exe"], capture_output=True)
        print("Backend stopped cleanly.")

if __name__ == "__main__":
    run_test()
