from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .release_policy import check_release_policy as _engine_check_release_policy
from .release_policy import format_release_policy_result


def check_release_policy_cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate release policy.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output", choices=("text", "json"), default="text")
    parser.add_argument("--release-tag", default="")
    parser.add_argument("--diff-base", default="")
    parser.add_argument("--diff-head", default="HEAD")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    result = _engine_check_release_policy(
        repo_root=repo_root,
        release_tag=args.release_tag,
        diff_base=args.diff_base,
        diff_head=args.diff_head,
    )
    print(result.to_json() if args.output == "json" else format_release_policy_result(result))
    return result.exit_code()


check_release_policy = check_release_policy_cli

if __name__ == "__main__":
    raise SystemExit(check_release_policy_cli(sys.argv[1:]))
