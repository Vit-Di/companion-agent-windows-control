import os
import sys
import subprocess
import uvicorn
import psutil
import socket
import time
import ctypes
from fastapi import FastAPI
from pydantic import BaseModel

# --- КОНФІГУРАЦІЯ (ХОВАЄМО КОНСОЛЬ В EXE) ---
IS_FROZEN = getattr(sys, 'frozen', False)

class DevNull:
    def write(self, msg): pass
    def flush(self): pass

if IS_FROZEN:
    sys.stdout = DevNull()
    sys.stderr = DevNull()

app = FastAPI(title="Church Agent Final")
PORT = 8001

# --- ШЛЯХИ ---
if IS_FROZEN:
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NIRCMD_PATH = os.path.join(BASE_DIR, "nircmd.exe")
HOSTNAME = socket.gethostname()

# --- CONSTANTS FOR SYSTEM CLICK & KEYBOARD (WINAPI) ---
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
WM_CHAR = 0x0102  # Для прямого вводу Unicode символів (UKR/ENG)

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

# --- ДОПОМІЖНІ ФУНКЦІЇ ---

def get_mouse_pos():
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return {"x": pt.x, "y": pt.y}

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'
    
def get_installed_apps():
    # Цей скрипт PowerShell сканує папки Пуск
    ps_script = r"""
    # --- ВАЖЛИВО: Встановлюємо кодування UTF-8 для коректного виводу кирилиці ---
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    
    $paths = @("$env:ProgramData\Microsoft\Windows\Start Menu\Programs", "$env:AppData\Microsoft\Windows\Start Menu\Programs")
    $sh = New-Object -ComObject WScript.Shell
    Get-ChildItem -Path $paths -Recurse -Include *.lnk | ForEach-Object { 
        try {
            $link = $sh.CreateShortcut($_.FullName)
            $target = $link.TargetPath
            if ($target -match "\.exe$") {
                Write-Output ($_.BaseName + "|" + $target)
            }
        } catch {}
    }
    """
    try:
        # Додаємо явний параметр encoding='utf-8' при запуску
        result = subprocess.run(
            ["powershell", "-Command", ps_script], 
            capture_output=True, 
            text=True, 
            encoding='utf-8', # <--- Це теж важливо
            creationflags=0x08000000
        )
        apps = []
        seen_names = set()
        
        for line in result.stdout.splitlines():
            if "|" in line:
                name, path = line.split("|", 1)
                name = name.strip()
                path = path.strip()
                if name not in seen_names and "uninstall" not in name.lower():
                    apps.append({"name": name, "path": path})
                    seen_names.add(name)
        
        return sorted(apps, key=lambda x: x['name'])
    except:
        return []

def send_unicode_text(text):
    """Надсилає текст прямо в активне вікно через WinAPI Message (найкраще для укр. мови)"""
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    for char in text:
        # Відправляємо код символу повідомленням SendMessageW
        ctypes.windll.user32.SendMessageW(hwnd, WM_CHAR, ord(char), 0)
        time.sleep(0.01)

# Створення файлу з IP при запуску
try:
    with open(os.path.join(BASE_DIR, "MY_IP.txt"), "w") as f:
        f.write(f"PC: {HOSTNAME}\nIP: {get_ip()}\nPORT: {PORT}")
except:
    pass

class ActionRequest(BaseModel):
    target: str = ""
    action: str = ""
    mode: str = "process"
    path: str = ""
    args: str = ""
    force: bool = False
    x: int = 0
    y: int = 0
    delay: float = 0.0
    text: str = ""

# --- ЕНДПОІНТИ ---

@app.get("/")
def check(): 
    return {"status": "online"}

@app.get("/stats")
def get_stats(check_process: str = ""):
    try:
        cpu = int(round(psutil.cpu_percent(interval=None)))
        ram = int(round(psutil.virtual_memory().percent))
        mouse = get_mouse_pos()
        proc_found = False
        if check_process:
            for p in psutil.process_iter(['name']):
                try:
                    if check_process.lower() in p.info['name'].lower():
                        proc_found = True
                        break
                except:
                    pass
        return {
            "hostname": HOSTNAME, 
            "cpu": cpu, 
            "ram": ram, 
            "mouse_x": mouse["x"], 
            "mouse_y": mouse["y"], 
            "process_found": proc_found
        }
    except:
        return {"hostname": "Error", "cpu": 0, "ram": 0, "process_found": False}

@app.get("/processes")
def list_processes():
    ignored = [
        'svchost.exe', 'conhost.exe', 'csrss.exe', 'wininit.exe', 'smss.exe', 
        'services.exe', 'lsass.exe', 'winlogon.exe', 'fontdrvhost.exe', 
        'dwm.exe', 'system', 'registry', 'idle'
    ]
    procs = set()
    for p in psutil.process_iter(['name']):
        try:
            name = p.info['name']
            if name and name.endswith('.exe') and name.lower() not in ignored:
                procs.add(name)
        except:
            pass
    return {"processes": sorted(list(procs))}

def run_cmd(cmd_str):
    if os.path.exists(NIRCMD_PATH):
        # creationflags=0x08000000 приховує консольне вікно при виклику nircmd всередині EXE
        subprocess.run(f'"{NIRCMD_PATH}" {cmd_str}', shell=True, creationflags=0x08000000)

@app.post("/keyboard/action")
def keyboard_action(r: ActionRequest):
    # А) Режим вводу тексту (Unicode метод)
    if r.action == "type":
        try:
            send_unicode_text(r.text)
            return {"status": "text_typed"}
        except:
            return {"status": "error"}

    # Б) Режим кнопок і хоткеїв (NirCmd)
    key = r.text.lower().replace(" ", "")
    if key == "spc": key = "space"
    if key == "esc": key = "escape"
    
    if key == "volume_mute":
        run_cmd("mutesysvolume 2")
    elif key == "volume_up":
        run_cmd("changesysvolume 2000")
    elif key == "volume_down":
        run_cmd("changesysvolume -2000")
    elif r.action == "hotkey":
        run_cmd(f"sendkeypress {key}")
    else:
        run_cmd(f"sendkey {key} press")
    
    return {"status": "key_sent", "key": key}

@app.post("/universal/control")
def universal_control(r: ActionRequest):
    if r.action in ["maximize", "minimize", "restore", "close_win", "focus"]:
        act_map = {"maximize":"max", "minimize":"min", "restore":"norm", "close_win":"close", "focus":"activate"}
        run_cmd(f"win {act_map.get(r.action)} process \"{r.path}\"")
    elif r.action == "kill":
        subprocess.run(f'taskkill /F /IM "{r.path}" /T', shell=True, creationflags=0x08000000)
    return {"status": "done"}

@app.post("/mouse/action")
def mouse_action(r: ActionRequest):
    if os.path.exists(NIRCMD_PATH):
        run_cmd(f"setcursor {r.x} {r.y}")
    else:
        ctypes.windll.user32.SetCursorPos(r.x, r.y)
    
    time.sleep(r.delay if r.delay > 0 else 0.05)

    if r.action == "click":
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    elif r.action == "dblclick":
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.1)
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    elif r.action == "rightclick":
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        
    return {"status": "clicked_hybrid"}

@app.post("/apps/start")
def app_start(r: ActionRequest):
    subprocess.Popen(f'"{r.path}" {r.args}', shell=True, creationflags=0x08000000)
    return {"status": "launched"}

@app.get("/apps/list")
def list_installed_apps():
    apps = get_installed_apps()
    return {"apps": apps}

@app.post("/system/power")
def power(r: ActionRequest):
    if r.action == "shutdown":
        os.system(f"shutdown /s {'/f' if r.force else ''} /t 0")
    elif r.action == "reboot":
        os.system(f"shutdown /r {'/f' if r.force else ''} /t 0")
    elif r.action == "logout":
        os.system(f"shutdown /l {'/f' if r.force else ''}")
    elif r.action == "lock":
        # Блокування екрану через системну DLL
        ctypes.windll.user32.LockWorkStation()
    elif r.action == "sleep":
        # Сон (використовуємо nircmd для надійності, якщо є, або rundll32)
        if os.path.exists(NIRCMD_PATH):
            run_cmd("standby")
        else:
            # Hibernate off, then suspend
            os.system("powercfg -h off")
            ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
            os.system("powercfg -h on")
            
    return {"status": "done", "action": r.action}

if __name__ == "__main__":
    # Порожня конфігурація логів, щоб уникнути помилок при запуску EXE
    empty_log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {},
        "handlers": {},
        "loggers": {},
    }
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=PORT, 
        log_config=empty_log_config if IS_FROZEN else None
    )