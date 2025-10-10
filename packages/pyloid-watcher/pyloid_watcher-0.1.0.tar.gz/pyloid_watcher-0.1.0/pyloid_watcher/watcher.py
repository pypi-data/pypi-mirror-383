import subprocess
import sys
import signal
import time
import os
import platform
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class PyloidWatcher(FileSystemEventHandler):
    def __init__(self, watch_path="src-pyloid", file_pattern="*.py", command=None, verbose=False):
        self.watch_path = Path(watch_path)
        self.file_pattern = file_pattern
        self.command = command or "uv run -p .venv ./src-pyloid/main.py"
        self.verbose = verbose
        self.process = None
        self.observer = None
        
        if not self.watch_path.exists():
            raise ValueError(f"감시 경로가 존재하지 않습니다: {self.watch_path}")
        
        # 초기 프로세스 시작
        self.restart()
    
    def log(self, message):
        if self.verbose:
            print(f"[WATCHER] {message}")
        else:
            print(message)
    
    def should_restart(self, event):
        """파일 변경 시 재시작 여부 결정"""
        if not event.src_path.endswith(self.file_pattern.replace("*", "")):
            return False
        
        # watch_path 내의 파일인지 확인
        try:
            Path(event.src_path).relative_to(self.watch_path)
            return True
        except ValueError:
            return False
    
    def on_modified(self, event):
        if self.should_restart(event):
            self.log(f"파일 변경 감지: {event.src_path}")
            self.restart()
    
    def restart(self):
        # 기존 프로세스 종료
        if self.process and self.process.poll() is None:
            self.log("기존 프로세스 종료 시도...")
            self._terminate_process(self.process)
        
        # 새 프로세스 시작
        self.log("Pyloid 앱 시작...")
        try:
            self.process = subprocess.Popen(
                self.command.split(),
                cwd=os.getcwd()
            )
        except Exception as e:
            self.log(f"실행 오류: {e}")
    
    def _terminate_process(self, process):
        """크로스플랫폼 프로세스 종료"""
        if platform.system() == "Windows":
            try:
                self.log(f"PID {process.pid} 강제 종료 시도...")
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)],
                             timeout=3, capture_output=True, check=True)
                self.log("프로세스 종료 성공")
            except subprocess.CalledProcessError as e:
                self.log(f"taskkill 실패, kill() 시도...")
                try:
                    process.kill()
                    process.wait(timeout=2)
                    self.log("kill()로 프로세스 종료 성공")
                except Exception as e2:
                    self.log(f"kill() 실패: {e2}")
            except subprocess.TimeoutExpired:
                self.log("taskkill 시간 초과, kill() 시도...")
                try:
                    process.kill()
                    process.wait(timeout=2)
                    self.log("kill()로 프로세스 종료 성공")
                except Exception as e:
                    self.log(f"kill() 실패: {e}")
        else:
            # Unix-like 시스템
            self.log(f"Unix 프로세스 PID {process.pid} 종료 시도...")
            process.terminate()
            try:
                process.wait(timeout=3)
                self.log("프로세스 종료 성공")
            except subprocess.TimeoutExpired:
                self.log("SIGTERM 실패, SIGKILL 사용...")
                process.kill()
                process.wait(timeout=2)
                self.log("SIGKILL로 프로세스 종료 성공")
    
    def start(self):
        """감시 시작"""
        self.observer = Observer()
        self.observer.schedule(self, path=str(self.watch_path), recursive=True)
        self.observer.start()
        
        def cleanup(signum, frame):
            self.log(f"종료 시그널 받음: {signum}")
            if self.observer:
                self.observer.stop()
            if self.process and self.process.poll() is None:
                self._terminate_process(self.process)
            if self.observer:
                self.observer.join()
            sys.exit(0)
        
        # 시그널 핸들러 등록
        if platform.system() == "Windows":
            signal.signal(signal.SIGINT, cleanup)
            signal.signal(signal.SIGBREAK, cleanup)
        else:
            signal.signal(signal.SIGTERM, cleanup)
            signal.signal(signal.SIGINT, cleanup)
        
        self.log(f"Pyloid 파일 감시 시작... (경로: {self.watch_path}, 패턴: {self.file_pattern})")
        self.log("Ctrl+C로 종료")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            cleanup(signal.SIGINT, None)