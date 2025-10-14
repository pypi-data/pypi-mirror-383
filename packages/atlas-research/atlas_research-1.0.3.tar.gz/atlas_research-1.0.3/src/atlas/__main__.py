# src/atlas/__main__.py
import argparse
import sys
from . import __version__
from .project import Atlas
from .visualize import export_pyvis


def main():
    parser = argparse.ArgumentParser(
        prog="atlas", description="Atlas — AI-Powered Research Network Framework (SaaS)"
    )

    # --- 전역 플래그 ---
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show the current Atlas version and exit.",
    )

    # --- 서브커맨드 구성 ---
    subparsers = parser.add_subparsers(dest="command", required=False)

    # atlas run --query "..."
    run_parser = subparsers.add_parser("run", help="Run Atlas query pipeline.")
    run_parser.add_argument("--query", type=str, help="Search query to analyze.")

    # atlas export
    subparsers.add_parser("export", help="Export visualization outputs.")

    args = parser.parse_args()

    # ✅ 버전 플래그 처리
    if args.version:
        print(f"Atlas v{__version__} — AI-Powered Research Network Framework (SaaS)")
        sys.exit(0)

    # ✅ 명령어 없이 실행 시 도움말 출력
    if not args.command:
        parser.print_help()
        sys.exit(0)

    # --- Run pipeline ---
    if args.command == "run":
        if not args.query:
            print("❗ Please provide a query using --query.")
            sys.exit(1)

        atlas = Atlas()
        atlas.run(args.query)

    elif args.command == "export":
        export_pyvis()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
