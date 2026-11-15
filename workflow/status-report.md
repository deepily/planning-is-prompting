# Status Report (canonical workflow)

**Purpose**: turn a one-line ask, *"status report on X"*, into a manager-level status document with a sense of humor. The document is written in the shape the podcast generator reads and piped straight into a five-minute `status_report` podcast. The asker names the topic and nothing else.

**When to use**: whenever the user asks where an initiative, plan, epic or repo stands: *"give me a status report on the code-health abstraction"*, *"progress report on the job runner, with a podcast"*. It also covers a broadcast asking every manager for a status report. Explicit fallback: `/plan-status-report <topic>`.

**Why it exists**: Rick, 14 Nov 2026, after asking for one the long way: *"so that I can ask for it simply as opposed to all of the circumlocution"*. The long way named the parts every time: where are we, what remains, the thinking behind each phase, the tricky parts, the open issues. Those parts are now the template, so the ask needs only the topic.

---

## Trigger phrases (for the Agent Skill description)

*"status report on X"*, *"give me a status report"*, *"progress report on X"*, *"status podcast on X"*, *"where are we on X, with a podcast"*. The topic is the only argument. With no topic, ask for one in a single `converse()` line; never guess it.

**Not triggers**: *"what's your status?"* or *"where are you?"* addressed to one session. Those ask about the session's own work and get a three-line answer, not a document.

---

## The steps

Each step ends with a result you can point at.

### 1. File the row

Run `task_create` for the report, quoting the ask in its body. The done line: "report in `io/tmp`, `status_report` podcast started or declined".
**Result:** a row id.

### 2. Read the sources and measure

Read the initiative's own records before writing a word:

| Source | How |
|---|---|
| The plan and its handoff | the `src/rnd/` document the initiative was built from |
| The store rows | `task_query( correlation_key="epic:<slug>", terse=True, include_terminal=True, include_parked=True )`, then `task_get` on the rows that are in progress or blocking, for their amendments |
| What landed | `git log` on the paths the plan names |
| Rulings | the Decisions Log in `TODO.md`, and rulings quoted in the plan |

Note the read time, because a store count is true only at the moment it was read. A figure you did not measure is labelled "not measured". Never write a guess beside measured figures.
**Result:** counts per phase (done, in progress, not started), each with its source.

### 3. Write the document in the template

The headings below are fixed. The podcast's digest step extracts six categories (done, outstanding, tricky, unresolved, blocked, next steps) and quotes a source line for each. A document that has these sections gets an accurate episode. One that hides them in prose gets a vague episode.

```markdown
# <Topic>: where we are (status report)

<Persona>, <date>, <time with zone>. <Who asked, and how>. Every figure comes from <sources, with read time>.

## The short version
<Verdict sentence. Counts: done / in progress / not started. Anything that changed since the asker last heard.>

## Phase by phase: status and the reasoning behind each
| Phase | Status | Why it is in this place |

## The tricky parts
<Numbered. What made each one hard, with its receipt.>

## Open questions, now and later
| Open item | Where it sits | When it bites |

## What happens next, in order
<Numbered. Then the recommendation, in one sentence.>
```

The *why it is in this place* column is the part that is easiest to drop and the part the asker most wants. Every phase exists for a reason (a ruling, a measured failure, a dependency). Say which.

A small Mermaid flow of the phases helps the reader. The podcast ignores it.
**Result:** the document, with every figure cited.

### 4. The voice: manager-level, with a sense of humor

The reader is a manager who wants the state of play in five minutes and likes being entertained a little on the way. Rick: *"because I'm a great fan of levity"*.

| Do | Don't |
|---|---|
| Make wry observations that come **from the facts**: *"13 of 14 steps are done. The fourteenth is the one that proves the other thirteen didn't break anything."* | Write a joke that bends a figure, rounds a date or implies progress that hasn't happened |
| Use wordplay in a heading or a closing line | Put a joke inside a table cell where a figure belongs |
| Use at most one light touch per section | Joke about a person, a seat's mistake or the user |
| Use plain English throughout, so the joke lands for a listener too | Use jargon, which makes even a good joke need a footnote |

Tables carry the facts. Humor lives in the prose around them. When a joke and accuracy disagree, cut the joke.
**Result:** the document reads in about five minutes and has at least one line worth repeating.

### 5. Place it where the podcast can read it

Write it to the **main checkout's** `io/tmp/` of the registered repo the initiative lives in, named `yyyy.mm.dd-<topic-slug>-status-<persona>.md`. The podcast tool refuses a file inside a git worktree, because the server cannot see it.

The document is transient, so it does **not** go in `src/rnd/`: a status report is a reading of the moment, not an authorized deliverable. A finding inside it that must outlive the file becomes a store row.
**Result:** an absolute path in a main checkout.

### 6. Pipe it into the podcast

```python
podcast_for_rick( path=<absolute path>, script_type="status_report" )
```

- The card it raises **is** the user's gate. Do not ask "shall I make a podcast?" first, because that would be two gates for one action.
- Leave `languages` empty for English unless the ask named others, for example `["en", "es-MX"]`.
- Leave `review` empty; a status report defaults to one shot.
- The tool blocks until the user answers, for up to about 15 minutes.

| Result | Then |
|---|---|
| `started` | record the `job_id` in the row |
| `declined` | the document stands alone; record that |
| `expired` or `default_used` | block the row on the user with a chase time, per `workflow/task-store-discipline.md` |
| `queue_failed` | retry with the same `card_id`; the card is still valid |

**Result:** a job id, or a recorded answer.

### 7. Deliver and close

- `notify()`: the spoken message is the verdict in three sentences. The abstract carries the doc-viewer link to the report (`workflow/doc-viewer-links.md`).
- Close the row with its receipts: the doc path, the job id and the read time. A manager seat closes with `manager_attestation`. A worker asks its manager to close it.

**Result:** a closed row.

---

## Checklist before declaring done

- [ ] Every figure has a source, and the read time is in the byline
- [ ] All five template sections are present, and each phase says why it is where it is
- [ ] Every joke rests on a fact and changes none
- [ ] The file is in a main checkout's `io/tmp/`, not a worktree and not `src/rnd/`
- [ ] `podcast_for_rick` was called with `script_type="status_report"` and its result is recorded
- [ ] The row is closed, or blocked with a chase time

---

## Integration

- **The podcast side**: the `status_report` script type lives in the podcast generator of the Lupin server. Its prompt decides how the two hosts sound, and the document's humor carries into the digest only as the facts it rests on. Asking the hosts themselves to lean into wordplay is a change to that prompt, made in that repo.
- **Broadcast asks**: when a broadcast asks every manager for a status report, each manager runs this workflow on its own board, as one document per manager.
- **Related**: `workflow/doc-viewer-links.md` (the link), `workflow/task-store-discipline.md` (the row and its receipts), `workflow/rnd-directory-policy.md` (why not `src/rnd/`), `workflow/brevity-mandate.md` (the spoken summary).
