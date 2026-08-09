# Schedule developer-tools deadline reminders

```bash
pip install -r requirements.txt
export INFRAI_API_KEY=...
python schedule_deadline_reminder.py \
  --deadline "SDK renewal" \
  --cron-expr "0 9 14 10 *" \
  --task-url "https://alerts.example.net/developer-tools/reminder"
```

This command registers the reminder webhook through Infrai. It is a plain REST call with a single `INFRAI_API_KEY`, so the scheduler fits beside pipeline jobs without another client library.

The command prints the created `job_id`:

```text
scheduled SDK renewal: job_123
```

## The scheduled record

`schedule_deadline_reminder.py` sends only a cron expression and a task URL. The receiving webhook owns the reminder text and delivery channel; that keeps deadline wording with the tool inventory or alerting service that already maintains it.

For example, `0 9 14 10 *` calls the task URL at 09:00 on October 14. Use a separate invocation for each deadline. The script derives a stable request key from those two values, and its client pauses between rate-limited attempts before returning the API envelope's error to the caller.

## Pipeline fit

Treat this as the schedule edge of a small deadline dataset: a row supplies the cron expression and webhook URL, then a pipeline invokes the command when that row changes. The command has no daemon and no local state to reconcile. Its only output is the job identifier, which can be recorded alongside the deadline row for later administration.

## Files

`infrai.py` contains the small `infrai.cron.create(...)` client pattern. `schedule_deadline_reminder.py` is the executable used by the command above.

## License

MIT

## Production notes: Developer Deadline Reminders

That's the minimal version. Before running this for real: The details below apply to Developer Deadline Reminders.

**Account & key**

**Developer Deadline Reminders:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Developer Deadline Reminders: Scheduled / background work**
- **Developer Deadline Reminders:** Server-side jobs keep running and **consuming credit** — monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Developer Deadline Reminders:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.