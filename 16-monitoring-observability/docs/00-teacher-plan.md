# Teacher Plan — Module 16: Monitoring & Observability

**Total time:** 3 hrs (180 min) — includes a 25 min buffer, partly because Alerts (topic 6) has real notification latency you can't rush.

## Before you start recording/teaching

- [ ] Module 14 complete
- [ ] `.env` filled in, `00_setup_vars.bat` + `00a_initial_setup.bat` already run
- [ ] Service already deployed before recording — don't burn camera time on a fresh deploy; jump straight to observing it
- [ ] Have your own email ready as the alert notification channel for topic 6
- [ ] Send a handful of normal + simulated-error + simulated-slow requests *before* recording, so topics 1-2 have real historical data to look at immediately instead of an empty console

## Suggested pacing (180 min)

| # | Topic | Minutes | Format |
|---|-------|---------|--------|
| 1 | Cloud Logging | 20 | Console tour of real logs |
| 2 | Cloud Monitoring | 20 | Console tour of built-in metrics |
| 3 | Error Reporting | 25 | Trigger `simulate_error`, watch it appear |
| 4 | Cloud Trace | 25 | Trigger `simulate_slow`, read the waterfall |
| 5 | Metrics | 20 | Look at the custom metric the app writes itself |
| 6 | Alerts | 25 | Set up a policy, trigger it, wait for the notification |
| 7 | Dashboards | 20 | Build one view combining everything |
| — | Buffer | 25 | — |

## Teaching order rationale

Keep the syllabus order — it happens to move from "just look at what's already there" (Logging, Monitoring) to "look at something going wrong" (Error Reporting, Trace) to "define your own signal" (Metrics) to "get proactively told" (Alerts) to "see it all at once" (Dashboards). Each topic builds the case for the next.

## Per-Component Focus

### 1. Cloud Logging
**Land this one idea:** "Every `logging.info()` call in the code becomes a real, searchable, filterable entry here — structured, not just a wall of text."
- Demo: send a normal request, find its log entry, point out the structured fields (feed URL, headline count) versus a plain print statement.
- Common confusion: students expect logs to appear instantly. There's usually a few seconds of ingestion delay — mention it so nobody panics.

### 2. Cloud Monitoring
**Land this one idea:** "You didn't write a single line of code for this — request count, latency, memory, it's all collected automatically the moment something's deployed on Cloud Run."
- Demo: open the service's built-in metrics in the Monitoring console, point at request count and latency graphs from the requests sent before recording.
- Common confusion: conflating this with topic 5 (Metrics). Say explicitly: this topic is what GCP gives you for free; topic 5 is what *you* define yourself.

### 3. Error Reporting
**Land this one idea:** "You didn't have to configure Error Reporting to catch this — it automatically scans logs for stack traces and groups them."
- Demo: call the service with `?simulate_error=true`, wait a few seconds, refresh Error Reporting, show the grouped error with its real stack trace.
- Common confusion: students think they need to manually report errors. For unhandled exceptions in a supported runtime, they don't — this is automatic.

### 4. Cloud Trace
**Land this one idea:** "This answers 'where did the time actually go,' and the answer is almost never where you'd guess."
- Demo: call with `?simulate_slow=true`, open the trace waterfall, show the `summarize_headlines` span dominating the timeline — then call normally and compare against a fast trace.
- Common confusion: expecting traces instantly. Same ingestion delay note as topic 1.

### 5. Metrics
**Land this one idea:** "`headlines_processed_total` didn't exist until the code explicitly wrote it — that's the difference from topic 2."
- Demo: after a few normal runs, show the custom metric's data points in the Monitoring console, filtered under `custom.googleapis.com/`.
- Common confusion: forgetting custom metrics need the exact `custom.googleapis.com/...` prefix and won't show up under the built-in metric list from topic 2.

### 6. Alerts
**Land this one idea:** "This is the payoff for everything so far — the moment monitoring stops being something you check and starts being something that checks you."
- Demo: create the log-based metric + alert policy, trigger `simulate_error` a couple of times, then **explicitly tell the audience "now we wait a minute or two"** rather than pretending it's instant — cut the recording if needed, but don't fake the timing.
- Common confusion: expecting instant notification. Alert evaluation and notification both have real latency — set that expectation up front.

### 7. Dashboards
**Land this one idea:** "One glance, not five separate console tabs — this is what you'd actually leave open during an on-call shift."
- Demo: deploy the dashboard JSON, walk through each tile, tie each one back to the topic that produced its data.

## Wrap-up

- Rapid-fire recap: one question from each topic's "Quick Recap" (7 questions)
- Reinforce the module's core lesson one more time: test your alarms before the real fire, not during it
- No "tease next module" — modules are being built out of order
