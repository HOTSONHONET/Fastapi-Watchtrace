import time

def log_event(message: str):
    now = time.strftime("%H:%M:%S")
    print(f"[{now}] {message}")