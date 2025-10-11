"""
Tasks Service - Task management operations
"""

import time
from typing import TYPE_CHECKING, Callable, Dict, List, Optional

from ..exceptions import TimeoutError
from ..types import AccountInfo, TaskResponse

if TYPE_CHECKING:
    from ..http_client import HttpClient


class Tasks:
    """Service for task management operations"""

    def __init__(self, http_client: "HttpClient") -> None:
        """
        Initialize Tasks service

        Args:
            http_client: HTTP client instance
        """
        self.http_client = http_client

    def get(self, task_id: str) -> TaskResponse:
        """
        Get the status of a task

        Args:
            task_id: The ID of the task to check

        Returns:
            Task response with current status

        Example:
            >>> task = client.tasks.get(task_id)
            >>> print(task['status'])  # 'pending', 'processing', 'completed', 'failed'
        """
        return self.http_client.post("/fetch", {"task_id": task_id})  # type: ignore

    def get_many(self, task_ids: List[str]) -> Dict[str, List[TaskResponse]]:
        """
        Get the status/results of multiple tasks

        Args:
            task_ids: Array of task IDs (min 2, max 20)

        Returns:
            Object containing array of task results/statuses

        Example:
            >>> result = client.tasks.get_many(['task_id_1', 'task_id_2'])
            >>> print(result['tasks'])
        """
        return self.http_client.post("/fetch-many", {"task_ids": task_ids})  # type: ignore

    def wait_for(
        self,
        task_id: str,
        on_progress: Optional[Callable[[int], None]] = None,
        interval: int = 3,
        timeout: int = 300,
    ) -> TaskResponse:
        """
        Wait for a task to complete with optional progress callback

        Args:
            task_id: The ID of the task to wait for
            on_progress: Optional callback function for progress updates
            interval: Polling interval in seconds (default: 3)
            timeout: Maximum wait time in seconds (default: 300 = 5 minutes)

        Returns:
            The completed task result

        Raises:
            TimeoutError: If task exceeds timeout
            Exception: If task fails

        Example:
            >>> result = client.tasks.wait_for(
            ...     task_id,
            ...     on_progress=lambda p: print(f'Progress: {p}%'),
            ...     interval=3,
            ...     timeout=300
            ... )
        """
        start_time = time.time()

        while True:
            # Check for timeout
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Task {task_id} timed out after {timeout}s")

            task = self.get(task_id)

            # Call progress callback if provided
            if on_progress and task.get("progress") is not None:
                on_progress(task["progress"])  # type: ignore

            # Check if task is completed
            if task.get("status") == "completed":
                return task

            # Check if task failed
            if task.get("status") == "failed":
                error_message = (
                    task.get("message") or task.get("error") or "Task failed without error message"
                )
                error = Exception(f"Task {task_id} failed: {error_message}")
                setattr(error, "task_details", task)
                raise error

            # Wait before polling again
            time.sleep(interval)

    def get_account_info(self) -> AccountInfo:
        """
        Get account information including credits, usage, plan, etc.

        Returns:
            Account information

        Example:
            >>> account = client.tasks.get_account_info()
            >>> print(f"Email: {account['email']}")
            >>> print(f"Credits: {account['credits']}")
            >>> print(f"Plan: {account['plan']}")
        """
        return self.http_client.get("/account")  # type: ignore

