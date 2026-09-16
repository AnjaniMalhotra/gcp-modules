# Teacher Plan — Module 13: Storage for AI Applications

**Total time:** 3 hrs (180 min) — includes 15 min buffer.
**Format:** Jupyter notebooks throughout, same style as Module 7. Two topics (Cloud SQL, Redis) need real infrastructure — same provisioning discipline as Module 9, but faster this time since the concepts (Cloud SQL Connector, bastion + SSH tunnel) are already taught.

## Before you start recording/teaching

- [ ] Modules 2, 3, 9 complete
- [ ] **Kick off `03a_provision_cloud_sql.bat` before recording** — still takes 5-10 minutes
- [ ] Have `04a_provision_redis_and_bastion.bat` and the SSH tunnel ready to go for topic 4 — same two-terminal-window setup as Module 9
- [ ] `.env` filled in
- [ ] `99_cleanup.bat` ready at the end

## Suggested pacing (180 min)

| # | Topic | Minutes | Format |
|---|-------|---------|--------|
| 1 | Cloud Storage | 25 | Notebook — CRUD on the Documents Vault |
| 2 | Firestore | 25 | Notebook — Student Profiles |
| 3 | Cloud SQL | 30 | Notebook — Student Attendance, JOIN query |
| 4 | Redis | 30 | Notebook — Cached AI Insights, timing demo |
| 5 | BigQuery | 35 | Notebook — public dataset + NL-to-SQL mini agent |
| 6 | Choosing the Right Storage | 20 | Notebook — comparison + scenario Q&A |
| — | Buffer | 15 | — |

## Teaching order rationale

Keep the syllabus order. It happens to move from simplest (Cloud Storage — just files) to most conceptually loaded (BigQuery — scale, cost model, and a small agent) before closing with the synthesis topic. Cloud SQL and Redis sit in the middle specifically so students already have Cloud Storage and Firestore as points of contrast when they hit the "why would I choose *this* over Firestore" question.

## Per-Component Focus

### 1. Cloud Storage
**Land this one idea:** "Object storage is for whole files, not records you'd want to query individually."
- Demo: upload a "report card," list the bucket, overwrite it (point out GCS has no partial update — it's always a full replace), generate a signed URL, delete it.
- Common confusion: students expect to "edit one field" of a stored file the way they would a database row. Clarify: that's not what object storage is for — that's Firestore/Cloud SQL's job.

### 2. Firestore
**Land this one idea:** "The shape of this data — nested, flexible, varies student to student — is exactly what Firestore is good at."
- Demo: create a student profile with a nested contact object and an extracurriculars array, query for all grade-10 students, `ArrayUnion` a new activity onto one profile.
- Common confusion: students try to force a rigid schema onto Firestore out of relational habit. Point out the *lack* of a fixed schema is the feature here, not a limitation.

### 3. Cloud SQL
**Land this one idea:** "The moment you need a JOIN, you need a relational database — Firestore genuinely can't do this cleanly."
- Demo: two related tables, then a JOIN query computing attendance % per student. This is the payoff moment — show the query, show how naturally it reads.
- Common confusion: students who liked Firestore's flexibility in topic 2 ask "why not just store attendance as an array field on the student document?" Good — that's exactly the discussion to have: at what point does that break down (many-to-many, aggregation across students, referential integrity)?

### 4. Redis
**Land this one idea:** "Caching an LLM call isn't optional polish — it's a real cost and latency lever in production."
- Demo: ask the same question about a student twice, live, and just... let the timing difference speak for itself. First call: a couple seconds. Second call: near-instant.
- Common confusion: students think caching means the answer might go stale. Discuss the TTL as the deliberate control for that — short enough to stay fresh, long enough to actually save money.

### 5. BigQuery
**Land this one idea:** "You pay for bytes SCANNED, not bytes returned — `LIMIT 10` still scans the whole column."
- This is the most conceptually dense topic in the module — don't rush the pricing model explanation before touching the mini agent.
- Demo sequence: run a dry-run query estimate first (show bytes-to-be-scanned), then the real query, then the NL-to-SQL mini agent asking a real question about the Hacker News dataset.
- Common confusion: assuming public datasets cost money to store. They don't — Google pays for that; you only pay for querying, and even that's free up to 1 TiB/month.

### 6. Choosing the Right Storage
**Land this one idea:** "This is a decision framework you'll use for the rest of your career, not a one-time lesson."
- Walk the comparison table, then run the 2-3 scenario questions live and have the class (or your future viewers) answer before revealing it.
- Close with the BigQuery callback: at what scale would this specific school's data actually justify BigQuery? (Years of attendance/grade history across many schools, not one school's current-year data.)

## Wrap-up

- Rapid-fire recap: one question from each topic's "Quick Recap" (6 questions)
- Run `99_cleanup.bat` live, narrate what's being torn down
- No "tease next module" — modules are being built out of order
