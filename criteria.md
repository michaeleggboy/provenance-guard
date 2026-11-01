# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---

## 1. False Positives

Of 10 pieces of writing I know were written by a human, **at most 3 are labelled
high-confidence AI**, and this holds in **each of the 3 trials** (e.g. 2, 3, 1
passes; 2, 4, 1 is a miss). A human piece labelled "unsure" does not count as a
false positive.

**Why this target:**

Being accused of using AI when you didn't is serious at worst and annoying at
best, so a false positive costs a writer far more than a missed detection costs
the site. That is why I want this well under half (5 in 10). I didn't go as low
as 1 or 2 in 10 because the model signal is noisy from run to run, and a target
that strict would force thresholds so cautious that almost no AI text ever gets
flagged. Three in ten is the most wrong accusations I'm willing to accept while
the system still does its job; the "unsure" label exists to catch the borderline
cases so they don't become accusations.

---

## 2. Score Spread

Using 5 pieces that are clearly AI-written and 5 that are clearly human-written,
the **average combined score of the AI pieces is at least 0.50 higher than the
average combined score of the human pieces**, in each of the 3 trials.

**Why this target:**

Combined scores run from 0.0 (confidently human) to 1.0 (confidently AI), with
0.5 in the middle. I'd consider a score around 0.25 solidly human and around 0.75
solidly AI, which is a gap of 0.50. If clearly-different texts can't get that far
apart, the signals aren't separating human from AI writing well enough for the
labels to mean anything, and small run-to-run noise would push pieces across the
thresholds.

---

## 3. Label Coverage

Across a test set of 10 pieces (a mix of human, AI, and mixed or edited writing),
**each of the three labels (high-confidence human, unsure, high-confidence AI)
appears at least once**, in each of the 3 trials.

**Why this target:**

A label that can never be produced is a gap in the design, not a feature. I
especially want "unsure" to be reachable: it is the middle ground that lets the
system point out possible AI use without jumping to a false accusation that
could have serious consequences for the writer. Checking this on every trial
makes sure a label isn't only reachable on a lucky run.

---

## 4. The Appeal Path

**Every appeal (10 out of 10) on a real `content_id`** returns a confirmation,
changes that item's status to `under_review`, and adds an appeal entry to the
log, while the original decision entry stays unchanged. An appeal with a missing
or unknown `content_id` returns a clear error and does not change any status.

**Why this target:**

The appeal is the only thing standing between a wrongly accused writer and
nothing at all, so it has to work every single time, not most of the time. The
original decision is kept so there is a record of what the system said and why
it was challenged. Rejecting unknown IDs with an error matters because a typo
that silently "succeeds" would leave the writer thinking they'd appealed when
nothing was recorded.

---

## 5. Bad Input

For each of these inputs to `/submit`, the service **never crashes**; it returns
a 4xx error with a message that says what was wrong and how to fix it, and
records the rejection in the log:

- `text` is missing from the request
- `text` is empty or only whitespace
- `text` is longer than 20,000 characters
- the body isn't valid JSON

All 4 cases must pass (4 out of 4).

**Why this target:**

I want the system to be robust and user-friendly. A crash or a vague error
leaves the writer stuck and makes the service look broken. A message like
"`text` is empty — paste the writing you want checked" tells them exactly what
to do. Logging the rejection means bad or abusive input leaves a trace instead
of disappearing. The 20,000-character limit is well above any normal submission
but stops someone from tying up the model with an enormous paste.

---


<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
