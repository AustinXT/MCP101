import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Optional

# Ensure 'src' is on sys.path so imports like 'github_mcp_server.*' work without installing the package
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


def print_section(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def ensure_token() -> None:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("[WARN] GITHUB_TOKEN is not set. You may hit rate limits (60 req/hour).")


async def run_tests():
    ensure_token()

    # Local imports after sys.path is configured to satisfy linting (avoid E402) and ensure proper resolution
    from github_mcp_server.tools.search_issues import SearchIssuesInput, search_issues
    from github_mcp_server.tools.get_issue_details import GetIssueDetailsInput, get_issue_details
    from github_mcp_server.tools.list_pull_requests import ListPullRequestsInput, list_pull_requests
    from github_mcp_server.tools.get_pull_request_details import (
        GetPullRequestDetailsInput,
        get_pull_request_details,
    )
    from github_mcp_server.tools.list_repository_contents import (
        ListRepositoryContentsInput,
        list_repository_contents,
    )
    from github_mcp_server.tools.get_file_content import GetFileContentInput, get_file_content
    from github_mcp_server.tools.search_code import SearchCodeInput, search_code
    from github_mcp_server.utils.errors import MCPError

    repo = "vercel/next.js"
    issue_number: Optional[int] = None
    pr_number: Optional[int] = None
    results: dict = {}

    # 1) search_issues
    print_section("1) search_issues")
    try:
        res = await search_issues(
            SearchIssuesInput(
                query=f"repo:{repo} is:issue label:bug state:open",
                limit=5,
                sort="created",
                order="desc",
                format="json",
                detail="detailed",
            )
        )
        data = json.loads(res)
        summary_si = {
            "total_count": data.get("total_count"),
            "first_item_keys": list(data.get("items", [{}])[0].keys()) if data.get("items") else [],
            "sample_html_url": data.get("items", [{}])[0].get("html_url") if data.get("items") else None,
        }
        print("search_issues result summary:")
        print(json.dumps(summary_si, indent=2, ensure_ascii=False))
        results["search_issues"] = {"summary": summary_si, "error": None}
        if data.get("items"):
            issue_number = data["items"][0].get("number")
            print(f"Picked issue_number: {issue_number}")
        else:
            print("[INFO] No issues found for query.")
    except MCPError as e:
        print(f"[ERROR] search_issues MCPError: {e.message} (code={e.code})")
        results["search_issues"] = {"summary": None, "error": {"message": e.message, "code": e.code, "details": e.details}}

    # 2) get_issue_details
    print_section("2) get_issue_details")
    try:
        if issue_number:
            res = await get_issue_details(
                GetIssueDetailsInput(
                    repository=repo,
                    issue_number=issue_number,
                    format="json",
                    detail="detailed",
                )
            )
            data = json.loads(res)
            print("get_issue_details fields:")
            keys = list(data.keys())
            summary_gid = {
                "keys": keys[:20],
                "title": data.get("title"),
                "state": data.get("state"),
                "user": data.get("user", {}).get("login"),
            }
            print(json.dumps(summary_gid, indent=2, ensure_ascii=False))
            results["get_issue_details"] = {"summary": summary_gid, "error": None}
        else:
            print("[SKIP] No issue_number available from search_issues.")
    except MCPError as e:
        print(f"[ERROR] get_issue_details MCPError: {e.message} (code={e.code})")
        results["get_issue_details"] = {"summary": None, "error": {"message": e.message, "code": e.code, "details": e.details}}

    # 3) list_pull_requests
    print_section("3) list_pull_requests")
    try:
        res = await list_pull_requests(
            ListPullRequestsInput(
                repository=repo,
                state="open",
                limit=5,
                sort="updated",
                direction="desc",
                format="json",
                detail="detailed",
            )
        )
        data = json.loads(res)
        if isinstance(data, list) and data:
            pr_number = data[0].get("number")
        summary_lpr = {
            "count": len(data) if isinstance(data, list) else None,
            "first_pr_number": pr_number,
            "first_pr_title": data[0].get("title") if isinstance(data, list) and data else None,
        }
        print("list_pull_requests sample:")
        print(json.dumps(summary_lpr, indent=2, ensure_ascii=False))
        results["list_pull_requests"] = {"summary": summary_lpr, "error": None}
    except MCPError as e:
        print(f"[ERROR] list_pull_requests MCPError: {e.message} (code={e.code})")
        results["list_pull_requests"] = {"summary": None, "error": {"message": e.message, "code": e.code, "details": e.details}}

    # 4) get_pull_request_details
    print_section("4) get_pull_request_details")
    try:
        if pr_number:
            res = await get_pull_request_details(
                GetPullRequestDetailsInput(
                    repository=repo,
                    pull_number=pr_number,
                    format="json",
                    detail="detailed",
                )
            )
            data = json.loads(res)
            summary_gprd = {
                "state": data.get("state"),
                "merged": data.get("merged"),
                "user": data.get("user", {}).get("login"),
                "changed_files": data.get("changed_files"),
                "commits": data.get("commits"),
            }
            print("get_pull_request_details fields:")
            print(json.dumps(summary_gprd, indent=2, ensure_ascii=False))
            results["get_pull_request_details"] = {"summary": summary_gprd, "error": None}
        else:
            print("[SKIP] No pr_number available from list_pull_requests.")
    except MCPError as e:
        print(f"[ERROR] get_pull_request_details MCPError: {e.message} (code={e.code})")
        results["get_pull_request_details"] = {"summary": None, "error": {"message": e.message, "code": e.code, "details": e.details}}

    # 5) list_repository_contents
    print_section("5) list_repository_contents")
    try:
        res = await list_repository_contents(
            ListRepositoryContentsInput(
                repository=repo,
                path="",
                format="json",
                detail="concise",
                recursive=False,
            )
        )
        data = json.loads(res)
        # data can be list (dir listing) or dict (file object)
        count = len(data) if isinstance(data, list) else 1
        summary_lrc = {
            "entries_count": count,
            "first_entry": data[0] if isinstance(data, list) and data else data,
        }
        print(json.dumps(summary_lrc, indent=2, ensure_ascii=False))
        results["list_repository_contents"] = {"summary": summary_lrc, "error": None}
    except MCPError as e:
        print(f"[ERROR] list_repository_contents MCPError: {e.message} (code={e.code})")
        results["list_repository_contents"] = {"summary": None, "error": {"message": e.message, "code": e.code, "details": e.details}}

    # 6) get_file_content
    print_section("6) get_file_content")
    try:
        res = await get_file_content(
            GetFileContentInput(
                repository=repo,
                path="README.md",
                format="json",
                detail="detailed",
            )
        )
        data = json.loads(res)
        summary_gfc = {
            "name": data.get("name"),
            "path": data.get("path"),
            "language": data.get("language"),
            "is_binary": data.get("is_binary", False),
            "decoded_content_sample": (data.get("decoded_content", "")[:120] if data.get("decoded_content") else None),
        }
        print(json.dumps(summary_gfc, indent=2, ensure_ascii=False))
        results["get_file_content"] = {"summary": summary_gfc, "error": None}
    except MCPError as e:
        print(f"[ERROR] get_file_content MCPError: {e.message} (code={e.code})")
        results["get_file_content"] = {"summary": None, "error": {"message": e.message, "code": e.code, "details": e.details}}

    # 7) search_code
    print_section("7) search_code")
    try:
        res = await search_code(
            SearchCodeInput(
                query="filename:README.md",
                repository=repo,
                limit=5,
                format="json",
                detail="detailed",
            )
        )
        data = json.loads(res)
        summary_sc = {
            "total_count": data.get("total_count"),
            "first_item_name": data.get("items", [{}])[0].get("name") if data.get("items") else None,
            "first_item_path": data.get("items", [{}])[0].get("path") if data.get("items") else None,
        }
        print(json.dumps(summary_sc, indent=2, ensure_ascii=False))
        results["search_code"] = {"summary": summary_sc, "error": None}
    except MCPError as e:
        print(f"[ERROR] search_code MCPError: {e.message} (code={e.code})")
        results["search_code"] = {"summary": None, "error": {"message": e.message, "code": e.code, "details": e.details}}

    # 8) Negative tests: invalid repository and missing file to capture error paths
    print_section("8) Negative tests")
    # 8a) search_issues with invalid repo
    try:
        res = await search_issues(
            SearchIssuesInput(
                query="repo:INVALID/REPO is:issue",
                limit=1,
                format="json",
                detail="concise",
            )
        )
        data = json.loads(res)
        summary_neg_si = {
            "total_count": data.get("total_count"),
            "items_sample": data.get("items", [])[:1],
        }
        print("search_issues with invalid repo (unexpected success):")
        print(json.dumps(summary_neg_si, indent=2, ensure_ascii=False))
        results["search_issues_invalid_repo"] = {"summary": summary_neg_si, "error": None}
    except MCPError as e:
        print(f"[EXPECTED ERROR] search_issues invalid repo: {e.message} (code={e.code})")
        results["search_issues_invalid_repo"] = {"summary": None, "error": {"message": e.message, "code": e.code, "details": e.details}}

    # 8b) get_file_content with non-existent file
    try:
        res = await get_file_content(
            GetFileContentInput(
                repository=repo,
                path="THIS_FILE_SHOULD_NOT_EXIST.md",
                format="json",
                detail="concise",
            )
        )
        data = json.loads(res)
        summary_neg_gfc = {
            "name": data.get("name"),
            "path": data.get("path"),
        }
        print("get_file_content non-existent file (unexpected success):")
        print(json.dumps(summary_neg_gfc, indent=2, ensure_ascii=False))
        results["get_file_content_missing_file"] = {"summary": summary_neg_gfc, "error": None}
    except MCPError as e:
        print(f"[EXPECTED ERROR] get_file_content missing file: {e.message} (code={e.code})")
        results["get_file_content_missing_file"] = {"summary": None, "error": {"message": e.message, "code": e.code, "details": e.details}}

    # Write structured results to file
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "tool_test_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[INFO] Structured results written to: {output_path}")


if __name__ == "__main__":
    asyncio.run(run_tests())