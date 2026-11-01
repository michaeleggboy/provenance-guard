# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->



---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:**
How surprised the model is by this text. Lower means more predictable.

**Why that might differ between human and AI writing:**
AI are determinstic probabilty machines
designed to output the most likely next word(s) based on context. Therefore, AI writing should be
more predictable.

**What it can't see:**
Deliberate style choices that might lead to higher or lower predictablity.

### Signal two — the style signal

**What it measures:**
Punctuation density, sentence length variablity, and unique word usage rate.

**Why that might differ between human and AI writing:**
AI writing is generally deemed to be more standardized in sentence length and word usage. Also, AI
tends to use more of certain punctuations specifically em dashes.

**What it can't see:**

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:**
Take a weighted average of the two signals. But if the two signals are more than
`DISAGREEMENT_GAP` apart, the result is held inside the "unsure" band. When the two
methods split, the service can't give a confident label either way. That leans
toward fewer false accusations (a writer whose style reads human isn't called AI
on the model signal alone). It also means AI text that games only one signal can't
get a confident "human" either.

**The numbers:** (all in `config.py`)

| Setting | Value |
|---|---|
| `WEIGHT_MODEL_SIGNAL` | 0.5 |
| `WEIGHT_STYLE_SIGNAL` | 0.5 |
| `DISAGREEMENT_GAP` | 0.30 (a gap of more than this counts as a split) |
| Split → combined score clamped to | `HUMAN_THRESHOLD + 0.01` … `AI_THRESHOLD − 0.01` (currently 0.36 – 0.64) |

Inside the style signal (`stylometry.py::STYLE_MEASURES`), each measure goes through a
logistic around a midpoint, then a weighted mean:

| Measure | Midpoint (scores 0.5) | Weight | Direction |
|---|---|---|---|
| sentence length spread (stdev / mean) | 0.35 | 0.5 | higher = more human |
| punctuation density (non-terminal marks per word) | 0.08 | 0.3 | higher = more human |
| type-token ratio (40-word moving average) | 0.88 | 0.2 | higher = more human |

Fewer than two sentences → style signal returns 0.5 (nothing to measure).

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**

AI-written text about remote work that mixes very short sentences ("But it isn't perfect.",
"Organizations that adapt will thrive.") with long, comma-heavy ones:

| model_score | style_score | gap | combined |
|---|---|---|---|
| 0.693 (AI) | 0.176 (human) | 0.52 | 0.435 → unsure |

The model signal still sees predictable word choices. The style signal is fooled by the
uneven sentence lengths and extra commas, which is exactly its blind spot: it measures
shape, not substance. With 0.5/0.5 weights the average already falls in the unsure band,
so the clamp didn't change this result. The clamp matters when the average would leave
the band despite a split (e.g. model 0.95, style 0.60 → average 0.775 = "AI"; with the
rule → 0.64 = unsure), and it keeps that guarantee if I change the weights later.

**Calibration — four deliberately chosen inputs (plus one more):**

| Input | model | style | combined | Reading |
|---|---|---|---|---|
| Clearly AI (generic "furthermore… in conclusion…") | 0.862 | 0.674 | 0.768 | AI ✓ |
| Clearly human (specific, personal, uneven) | 0.360 | 0.111 | 0.236 | human ✓ |
| Formal human (committee/jurist prose) | 0.632 | 0.319 | 0.476 | unsure |
| Lightly-edited AI (casual rewording of the AI text) | 0.608 | 0.469 | 0.538 | unsure |
| Plain human ("I went to the store today…") | 0.876 | 0.768 | 0.822 | **AI ✗** |

The surprise was the formal human text: the model signal put it at 0.63, leaning AI, not
human as I expected. Style read it correctly (long varied sentences, semicolons), and the
average pulled it back to unsure. The real failure is plain human writing. *Both* signals
call it AI, so they agree and no combining rule can catch it. That's the false positive
this service is most likely to produce, against the writers least able to argue back.



---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human |  |  |
| unsure |  |  |
| high-confidence AI |  |  |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->



---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

*(Run on port 5050 with `PORT=5050 python app.py` — macOS AirPlay Receiver holds 5000.
This is the Milestone 3 response: one signal, `confidence`/`label`/`style_score` still placeholders.)*

```bash
$ curl -X POST http://127.0.0.1:5050/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "Artificial intelligence has revolutionized numerous industries by enabling more efficient processes and data-driven decision-making. Furthermore, it is important to note that these technologies offer significant benefits across a wide range of applications.", "creator_id": "michael"}'
```

```json
{"confidence":null,"content_id":"0e86282b-ef15-4226-b98d-616646e40642","guess":"ai","label":"pending","model_score":0.8394,"style_score":null}
```

A malformed submission gets a 400 and a log entry instead of a crash:

```bash
$ curl -X POST http://127.0.0.1:5050/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "", "creator_id": "michael"}'
```

```json
{"error":"bad_request","message":"'text' must be a non-empty string."}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "...", "reasoning": "..."}'
```

```json

```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5050/log?limit=2"
```

```json
{"count":2,"entries":[{"combined_score":null,"content_id":"0e86282b-ef15-4226-b98d-616646e40642","creator_id":"michael","guess":"ai","label":null,"model_score":0.8394,"status":"decided","style_score":null,"timestamp":"2026-11-01T17:53:23+00:00"},{"creator_id":"michael","event":"rejected","reason":"missing_text","status":"rejected","timestamp":"2026-11-01T17:53:23+00:00"}]}
```

---

## How I Used AI

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
