#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import logging
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_VERIFY_PROMPT = (
    "Run tests and verify only the changes made for the last task.\n"
    "Do not modify code unless something is broken.\n"
    "Summarize verification results.\n"
    "If tests fail, explain exactly what failed."
)

STATE_DIR_NAME = ".codex-runner"
STATE_FILE_NAME = "state.json"
LOGS_DIR_NAME = "logs"

# 👇 Ignore runner internal files
DEFAULT_IGNORE_PATTERNS = [".codex-runner/"]


@dataclass
class Task:
    task_id: int
    phase: str
    title: str
    status: str
    acceptance_criteria: list[str]
    notes: list[str]
    prompt_hint: str = ""


class RunnerError(Exception):
    pass


class CodexPortfolioRunner:
    def __init__(
        self,
        repo_root: Path,
        tasks_file: Path,
        max_tasks: int,
        verify_prompt: str,
        codex_cmd: str,
        extra_codex_args: list[str] | None = None,
        require_clean_git: bool = True,
        auto_commit: bool = True,
        auto_push: bool = True,
        dry_run: bool = False,
    ) -> None:
        self.repo_root = repo_root.resolve()
        self.tasks_file = tasks_file.resolve()
        self.max_tasks = max_tasks
        self.verify_prompt = verify_prompt
        self.codex_cmd = codex_cmd
        self.extra_codex_args = extra_codex_args or []
        self.require_clean_git = require_clean_git
        self.auto_commit = auto_commit
        self.auto_push = auto_push
        self.dry_run = dry_run

        self.state_dir = self.repo_root / STATE_DIR_NAME
        self.logs_dir = self.state_dir / LOGS_DIR_NAME
        self.state_file = self.state_dir / STATE_FILE_NAME

        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        self.logger = self._build_logger()

    def _build_logger(self) -> logging.Logger:
        logger = logging.getLogger("codex_portfolio_runner")
        logger.setLevel(logging.INFO)
        logger.handlers.clear()

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(formatter)
        logger.addHandler(console)

        file_handler = logging.FileHandler(
            self.logs_dir / f"runner-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.log",
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger

    def run(self) -> int:
        self.logger.info("Repo root: %s", self.repo_root)
        self.logger.info("Tasks file: %s", self.tasks_file)

        self._validate_environment()

        tasks = self._load_tasks()
        state = self._load_state()

        pending = [
            t for t in tasks
            if t.task_id not in state["completed_task_ids"]
            and t.status != "completed"
        ]

        if not pending:
            self.logger.info("No pending tasks found.")
            return 0

        tasks_to_run = pending[: self.max_tasks]

        for task in tasks_to_run:
            self.logger.info("=" * 80)
            self.logger.info("Starting Task %s - %s", task.task_id, task.title)

            # 👇 capture files before task
            files_before = set(self._get_changed_files())

            # Run Codex task
            task_result = self._run_codex_step("task", task, self._build_task_prompt(task))
            if task_result["returncode"] != 0:
                return task_result["returncode"]

            # Verify
            verify_result = self._run_codex_step("verify", task, self.verify_prompt)
            if verify_result["returncode"] != 0:
                return verify_result["returncode"]

            # 👇 capture files after task
            files_after = set(self._get_changed_files())
            changed_files = sorted(files_after - files_before)

            # remove tasks.json (auto update)
            rel_tasks = str(self.tasks_file.relative_to(self.repo_root))
            if rel_tasks in changed_files:
                changed_files.remove(rel_tasks)

            # Commit only task-related files
            if self.auto_commit:
                self._commit_task_changes(task, changed_files)

            self._mark_task_complete_in_json(task.task_id)

            state["completed_task_ids"].append(task.task_id)
            self._save_state(state)

            time.sleep(1)

        return 0

    # ---------------------------
    # Helpers
    # ---------------------------

    def _validate_environment(self) -> None:
        if not self.tasks_file.exists():
            raise RunnerError(f"Tasks file not found: {self.tasks_file}")

        if not (self.repo_root / ".git").exists():
            raise RunnerError("Not a git repo")

        if self.require_clean_git and not self._git_is_clean():
            raise RunnerError("Git working tree is not clean.")

    def _git_is_clean(self) -> bool:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() == ""

    def _load_tasks(self) -> list[Task]:
        raw = json.loads(self.tasks_file.read_text())
        return [
            Task(
                task_id=item["task_id"],
                phase=item.get("phase", ""),
                title=item["title"],
                status=item.get("status", ""),
                acceptance_criteria=item.get("acceptance_criteria", []),
                notes=item.get("notes", []),
            )
            for item in raw
        ]

    def _load_state(self) -> dict:
        if not self.state_file.exists():
            return {"completed_task_ids": []}
        return json.loads(self.state_file.read_text())

    def _save_state(self, state: dict):
        self.state_file.write_text(json.dumps(state, indent=2))

    def _run_codex_step(self, step_type, task, prompt):
        cmd = shlex.split(self.codex_cmd) + ["exec", prompt]

        result = subprocess.run(
            cmd,
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )

        return {"returncode": result.returncode}

    def _commit_task_changes(self, task: Task, files: list[str]):
        if not files:
            self.logger.info("No changes to commit.")
            return

        subprocess.run(["git", "add", "--"] + files, cwd=self.repo_root)

        subprocess.run(
            ["git", "commit", "-m", f"feat(task-{task.task_id}): {task.title}"],
            cwd=self.repo_root,
        )

    def _mark_task_complete_in_json(self, task_id: int):
        raw = json.loads(self.tasks_file.read_text())
        for item in raw:
            if item["task_id"] == task_id:
                item["status"] = "completed"
        self.tasks_file.write_text(json.dumps(raw, indent=2))

    def _get_changed_files(self):
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        files = []
        for line in result.stdout.splitlines():
            path = line[3:].strip()
            if any(path.startswith(p) for p in DEFAULT_IGNORE_PATTERNS):
                continue
            files.append(path)
        return files

    def _build_task_prompt(self, task: Task) -> str:
        return f"""
Open docs/TASKS.md and execute ONLY Task {task.task_id}.

Task: {task.title}

Do not start later tasks.

Output:
1. Plan
2. Changes
3. Files
4. Verification
5. Completed?
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--tasks-file", default="tools/tasks.json")
    parser.add_argument("--max-tasks", type=int, default=5)
    parser.add_argument("--verify-prompt-file", default="")
    parser.add_argument("--codex-cmd", default="codex")

    args = parser.parse_args()

    verify_prompt = DEFAULT_VERIFY_PROMPT

    runner = CodexPortfolioRunner(
        repo_root=Path(args.repo_root),
        tasks_file=Path(args.tasks_file),
        max_tasks=args.max_tasks,
        verify_prompt=verify_prompt,
        codex_cmd=args.codex_cmd,
    )

    sys.exit(runner.run())


if __name__ == "__main__":
    main()