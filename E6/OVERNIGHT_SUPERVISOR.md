# Overnight supervision

Run `python3 E6/overnight_supervisor.py` from the repository. It uses only the
standard library and macOS pmset, lsof and caffeinate. Supervisor events append
to `E6/supervision/events.jsonl`, outside experiment results. A nonblocking flock
prevents duplicate supervisors; existing TEST locks remain authoritative.

The supervisor checks frozen readiness, exact run binding, battery above 20%,
and live identity. It attaches to the existing output lock owner, or starts the
existing TEST command through a cooperative wrapper. No experiment source,
prompt, policy, checkpoint identity or results are changed. A denied localhost
identity read permits **attachment only**, with a logged verification limitation;
it never permits a new TEST launch. Identity mismatches always fail closed.

Battery is checked every 60 seconds. At <=20%, or an unreadable battery, it sends
SIGINT only to the confirmed TEST lock owner. New wrapped launches defer SIGINT
until the current request is saved in the exact-request cache, then exit before
the next request. Partial batch results are recovered from that cache on resume.
Already-running uninstrumented TEST cannot gain a cooperative handler externally:
SIGINT stops its serial scheduler, but may interrupt its current request. Its
existing intent marker is preserved and retain-invalid prevents any retry.
Completed checkpoints remain intact; no manual result writes occur.

Caffeinate -i prevents idle system sleep on AC and battery. Its -w assertion is
bound to TEST's PID, and the supervisor releases it when TEST exits. It does not
prevent lid-close sleep, shut down macOS, or kill Ollama. There is no automatic
TEST restart after exit. A supervisor error is logged and requires inspection.

Signal permission is checked with signal 0 before attaching. A restricted agent
sandbox may deny both localhost identity reads and signaling an existing TEST.
Such an environment cannot provide safe low-battery shutdown. Run this supervisor
from a normal macOS Terminal instead; never interpret monitoring alone as verified
battery protection. The initial deployed monitor predates this permission gate;
its limitation is recorded explicitly in the supervisor event log.
