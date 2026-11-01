"""
Signal two: the style signal. ← YOU BUILD THIS IN MILESTONE 4

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures are stubbed below because the brief names those three. They are
stubs, not implementations: what they compute is yours, and so is how you
combine them.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import math
import re
import statistics

TTR_WINDOW = 40   # words per window for the moving-average type-token ratio


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures — YOU BUILD THESE ─────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    How much sentence length varies. ← TODO

    Returns:
        A float. Decide yourself what scale it's on and which direction means
        "more human" — then write that down, because your combining rule
        depends on knowing it.

    A hint on what you're reaching for: the standard deviation of sentence
    lengths, probably divided by the mean so a long text and a short one are
    comparable. `statistics.stdev` is imported for you.

    Watch the edge case: a one-sentence submission has no spread at all, and
    `stdev` raises on fewer than two values. Decide what that should return
    before the attack set decides for you.

    Mine: coefficient of variation (stdev / mean) of words per sentence.
    0.0 = every sentence the same length; ~0.6+ is lumpy. **Higher = more
    human.** Fewer than two sentences returns None — no evidence either way,
    and style_signal treats it as neutral rather than as "perfectly even".
    """
    lengths = [len(words(s)) for s in sentences(text)]
    lengths = [n for n in lengths if n > 0]
    if len(lengths) < 2:
        return None
    mean = statistics.mean(lengths)
    return round(statistics.stdev(lengths) / mean, 4)


def type_token_ratio(text: str) -> float:
    """
    Unique words over total words. ← TODO

    Returns:
        A float between 0 and 1. Higher means more varied vocabulary.

    Worth knowing before you rely on it: this measure falls as text gets
    longer, because common words repeat. Two texts of different lengths aren't
    directly comparable on it, and if your test inputs vary a lot in length,
    that alone can look like a signal.

    Mine: a moving-average TTR (MATTR) — the plain ratio inside every
    TTR_WINDOW-word window, averaged — so a 60-word and a 300-word text are on
    the same footing. Shorter than one window falls back to the plain ratio.
    **Higher = more human.** No words returns None.
    """
    tokens = words(text)
    if not tokens:
        return None
    if len(tokens) <= TTR_WINDOW:
        return round(len(set(tokens)) / len(tokens), 4)
    ratios = [
        len(set(tokens[i:i + TTR_WINDOW])) / TTR_WINDOW
        for i in range(len(tokens) - TTR_WINDOW + 1)
    ]
    return round(statistics.mean(ratios), 4)


def punctuation_density(text: str) -> float:
    """
    How much punctuation, relative to length. ← TODO

    Returns:
        A float. Whether you count all punctuation or only some kinds — commas,
        semicolons, dashes — is a real choice. Semicolons and em dashes are
        more interesting than full stops, because they vary more between
        writers.

    Mine: non-terminal punctuation (, ; : — – - ( ) " ' ! ?) per word, so full
    stops — which only track sentence count — don't count. Apostrophes inside
    words (don't) aren't counted either. Direction is set in style_signal.
    """
    tokens = words(text)
    if not tokens:
        return None
    marks = re.findall(r"[,;:—–()\"“”!?]|(?<!\w)'|'(?!\w)|\s-\s", text)
    return round(len(marks) / len(tokens), 4)


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """
    The style signal as a 0–1 score. **Higher means more likely AI.** ← TODO

    Combine your three measures into one number. Same direction as
    `detector.model_signal`, so that `scoring.combine_signals` can treat them
    the same way — if one of your signals runs backwards, everything above it
    is wrong in a way that's hard to see.

    Two things to decide and write down:

      1. Which direction each measure points. Low spread means more AI-ish, so
         it needs flipping. Work out which of your three need that.
      2. How to get each onto a comparable scale. A raw type-token ratio sits
         between 0 and 1; a raw punctuation count doesn't. Adding them
         unscaled means whichever has the bigger numbers wins by default.

    Test it on the four calibration inputs from Milestone 4 — clearly AI,
    clearly human, plain conventional human writing, lightly-edited AI — before
    you trust it. Plain and ordinary, not formal: formal prose reads as *human*
    to signal one, and it is plain writing that gets accused.

    Mine: every measure points "higher = more human", so each goes through a
    flipped logistic onto 0–1 AI-ness — 0.5 at its midpoint, steepness picked
    from the calibration texts — then a weighted mean.

    Fewer than two sentences returns 0.5: one sentence has no shape to
    measure, and letting the other two decide alone scored a single
    comma-heavy sentence as ~0.03 "human" — a free pass for anyone who
    writes everything as one sentence.
    """
    if sentence_length_spread(text) is None:
        return 0.5

    parts = []
    for measure, midpoint, steepness, weight in STYLE_MEASURES.values():
        value = measure(text)
        if value is None:
            continue
        ai_ness = 1.0 / (1.0 + math.exp(steepness * (value - midpoint)))
        parts.append((weight, ai_ness))

    if not parts:
        return 0.5
    total = sum(w for w, _ in parts)
    return round(sum(w * a for w, a in parts) / total, 4)


# measure: (function, midpoint, steepness, weight). The midpoint is the raw
# value that scores 0.5 — chosen between the clearly-AI and clearly-human
# calibration texts. TTR barely separates them at these lengths, so it counts
# least.
STYLE_MEASURES = {
    "sentence_length_spread": (sentence_length_spread, 0.35, 8.0, 0.5),
    "punctuation_density": (punctuation_density, 0.08, 50.0, 0.3),
    "type_token_ratio": (type_token_ratio, 0.88, 25.0, 0.2),
}


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
