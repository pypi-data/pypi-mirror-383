import argparse
import sys
from pathlib import Path
from .watcher import PyloidWatcher

def main():
    parser = argparse.ArgumentParser(
        description="Pyloid 백엔드 파일 감시자",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  pyloid-watcher                    # 현재 디렉토리 감시
  pyloid-watcher --path ./src      # 특정 경로 감시
  pyloid-watcher --pattern "*.py"  # 파일 패턴 지정
        """
    )
    
    parser.add_argument(
        "--path", "-p",
        type=str,
        default="src-pyloid",
        help="감시할 디렉토리 경로 (기본값: src-pyloid)"
    )
    
    parser.add_argument(
        "--pattern", "-t",
        type=str,
        default="*.py",
        help="감시할 파일 패턴 (기본값: *.py)"
    )
    
    parser.add_argument(
        "--command", "-c",
        type=str,
        default="uv run -p .venv ./src-pyloid/main.py",
        help="재시작할 명령어"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="상세한 로그 출력"
    )
    
    args = parser.parse_args()
    
    try:
        watcher = PyloidWatcher(
            watch_path=args.path,
            file_pattern=args.pattern,
            command=args.command,
            verbose=args.verbose
        )
        watcher.start()
    except KeyboardInterrupt:
        print("\n감시 중지")
        sys.exit(0)
    except Exception as e:
        print(f"오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()