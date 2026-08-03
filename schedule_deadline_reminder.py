"""Register a webhook reminder for a developer-tools deadline."""

import argparse

import infrai


def schedule_deadline_reminder(cron_expr: str, task_url: str) -> str:
    """Register the reminder and return its Infrai job identifier."""
    job = infrai.cron.create(cron_expr=cron_expr, task=task_url)
    return job["job_id"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Schedule a deadline reminder webhook with Infrai."
    )
    parser.add_argument(
        "--cron-expr",
        required=True,
        help="Five-part cron expression for the reminder in the task's schedule.",
    )
    parser.add_argument(
        "--task-url",
        required=True,
        help="HTTPS webhook that receives the reminder request.",
    )
    parser.add_argument(
        "--deadline",
        required=True,
        help="Label printed with the scheduled job.",
    )
    args = parser.parse_args()

    job_id = schedule_deadline_reminder(args.cron_expr, args.task_url)
    print(f"scheduled {args.deadline}: {job_id}")


if __name__ == "__main__":
    main()
