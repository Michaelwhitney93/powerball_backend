import random
import statistics
import warnings
from collections import defaultdict
from datetime import datetime, timedelta


TRAILING_DAYS = 365


# ── Sampling utilities ────────────────────────────────────────────────────────

def _weighted_sample(weights: dict) -> int:
    if not weights:
        raise ValueError("Empty weight dict")
    numbers = list(weights.keys())
    vals = list(weights.values())
    total = sum(vals)
    if total <= 0:
        return random.choice(numbers)
    r = random.uniform(0, total)
    cumulative = 0.0
    for n, w in zip(numbers, vals):
        cumulative += w
        if r <= cumulative:
            return n
    return numbers[-1]


def _pick_five(weights: dict) -> list:
    remaining = dict(weights)
    picked = []
    for _ in range(5):
        n = _weighted_sample(remaining)
        picked.append(n)
        del remaining[n]
    return sorted(picked)


def _freq_to_weights(counts: dict) -> dict:
    total = sum(counts.values()) or 1
    return {n: c / total for n, c in counts.items() if c > 0}


def _fill_white(weights: dict) -> dict:
    if not weights:
        return {n: 1 / 69 for n in range(1, 70)}
    floor = min(weights.values()) * 0.1
    return {n: weights.get(n, floor) for n in range(1, 70)}


def _fill_pb(weights: dict) -> dict:
    if not weights:
        return {n: 1 / 26 for n in range(1, 27)}
    floor = min(weights.values()) * 0.1
    return {n: weights.get(n, floor) for n in range(1, 27)}


# ── Data helpers ──────────────────────────────────────────────────────────────

def _white_freq(drawings, filt=None) -> dict:
    counts = defaultdict(int)
    for d in drawings:
        if filt and not filt(d):
            continue
        for ball in [d.first_ball, d.second_ball, d.third_ball, d.fourth_ball, d.fifth_ball]:
            if ball is not None:
                counts[ball] += 1
    return dict(counts)


def _pb_freq(drawings, filt=None) -> dict:
    counts = defaultdict(int)
    for d in drawings:
        if filt and not filt(d):
            continue
        if d.power_ball is not None:
            counts[d.power_ball] += 1
    return dict(counts)


def _white_weights(drawings, filt=None) -> dict:
    return _fill_white(_freq_to_weights(_white_freq(drawings, filt)))


def _pb_weights(drawings, filt=None) -> dict:
    return _fill_pb(_freq_to_weights(_pb_freq(drawings, filt)))


# ── Constraint builders ───────────────────────────────────────────────────────
# Each builder returns a factory; calling the factory returns a fresh constraint
# function with a locked-in target for that generation attempt.
# These are public so any algorithm can be wrapped with them via make_constrained.

def sum_range_builder(drawings):
    sums = []
    for d in drawings:
        balls = [d.first_ball, d.second_ball, d.third_ball, d.fourth_ball, d.fifth_ball]
        if all(b is not None for b in balls):
            sums.append(sum(balls))
    if len(sums) < 2:
        return lambda: (lambda _: True)
    mean = statistics.mean(sums)
    std = statistics.stdev(sums)
    lo, hi = mean - std, mean + std

    def factory():
        return lambda balls: lo <= sum(balls) <= hi

    return factory


def odd_even_builder(drawings):
    profile_counts = defaultdict(int)
    for d in drawings:
        balls = [d.first_ball, d.second_ball, d.third_ball, d.fourth_ball, d.fifth_ball]
        if all(b is not None for b in balls):
            odd = sum(1 for b in balls if b % 2 == 1)
            high = sum(1 for b in balls if b > 34)
            profile_counts[(odd, high)] += 1
    if not profile_counts:
        return lambda: (lambda _: True)

    def factory():
        target = _weighted_sample(dict(profile_counts))

        def constraint(balls):
            odd = sum(1 for b in balls if b % 2 == 1)
            high = sum(1 for b in balls if b > 34)
            return (odd, high) == target

        return constraint

    return factory


def make_constrained(gen_fn, constraint_factories, max_retries=300):
    def constrained():
        constraints = [f() for f in constraint_factories]
        for _ in range(max_retries):
            white, pb = gen_fn()
            if all(c(white) for c in constraints):
                return white, pb
        warnings.warn(
            f"{gen_fn.__name__}: constraint not satisfied after {max_retries} retries; returning unconstrained result"
        )
        return gen_fn()

    constrained.__name__ = gen_fn.__name__ + "_constrained"
    return constrained


# ── Algorithm factories ───────────────────────────────────────────────────────

def make_hot_numbers(drawings):
    """#1 — frequency-weighted over trailing 12 months."""
    cutoff = datetime.now() - timedelta(days=TRAILING_DAYS)
    recent = [d for d in drawings if d.date_drawn and d.date_drawn >= cutoff] or drawings
    ww = _white_weights(recent)
    pw = _pb_weights(recent)

    def generate():
        return _pick_five(ww), _weighted_sample(pw)

    generate.__name__ = "hot_numbers"
    return generate


def make_cold_numbers(drawings):
    """#2 — inverse frequency over trailing 12 months (gambler's fallacy)."""
    cutoff = datetime.now() - timedelta(days=TRAILING_DAYS)
    recent = [d for d in drawings if d.date_drawn and d.date_drawn >= cutoff] or drawings
    wc = _white_freq(recent)
    pc = _pb_freq(recent)
    max_w = max(wc.values(), default=1) + 1
    max_p = max(pc.values(), default=1) + 1
    ww = _fill_white(_freq_to_weights({n: max_w - wc.get(n, 0) for n in range(1, 70)}))
    pw = _fill_pb(_freq_to_weights({n: max_p - pc.get(n, 0) for n in range(1, 27)}))

    def generate():
        return _pick_five(ww), _weighted_sample(pw)

    generate.__name__ = "cold_numbers"
    return generate


def make_position_specific(drawings):
    """#3 — separate frequency table per ball position."""
    pos_weights = []
    for col in ["first_ball", "second_ball", "third_ball", "fourth_ball", "fifth_ball"]:
        counts = defaultdict(int)
        for d in drawings:
            val = getattr(d, col)
            if val is not None:
                counts[val] += 1
        pos_weights.append(_fill_white(_freq_to_weights(dict(counts))))
    pw = _pb_weights(drawings)

    def generate():
        picked = []
        for w in pos_weights:
            available = {n: v for n, v in w.items() if n not in picked}
            picked.append(_weighted_sample(available))
        return sorted(picked), _weighted_sample(pw)

    generate.__name__ = "position_specific"
    return generate


def make_markov_chain(drawings):
    """#4 — each position conditioned on the previous via transition frequencies."""
    cols = ["first_ball", "second_ball", "third_ball", "fourth_ball", "fifth_ball"]

    first_counts = defaultdict(int)
    for d in drawings:
        if d.first_ball is not None:
            first_counts[d.first_ball] += 1
    first_w = _fill_white(_freq_to_weights(dict(first_counts)))

    # transitions[i][from_num][to_num] = count for position i → i+1
    transitions = []
    for i in range(4):
        mat = defaultdict(lambda: defaultdict(int))
        for d in drawings:
            fv = getattr(d, cols[i])
            tv = getattr(d, cols[i + 1])
            if fv is not None and tv is not None:
                mat[fv][tv] += 1
        transitions.append({k: dict(v) for k, v in mat.items()})

    pw = _pb_weights(drawings)

    def generate():
        picked = []
        picked.append(_weighted_sample(first_w))
        for trans in transitions:
            from_num = picked[-1]
            to_counts = {k: v for k, v in trans.get(from_num, {}).items() if k not in picked}
            if to_counts:
                w = _fill_white(_freq_to_weights(to_counts))
                w = {k: v for k, v in w.items() if k not in picked}
            else:
                w = {n: 1 for n in range(1, 70) if n not in picked}
            picked.append(_weighted_sample(w))
        return sorted(picked), _weighted_sample(pw)

    generate.__name__ = "markov_chain"
    return generate


def make_hot_pairs(drawings):
    """#5 — co-occurrence clustering; anchor on the strongest historical pairs."""
    cooc = defaultdict(lambda: defaultdict(int))
    for d in drawings:
        balls = [b for b in [d.first_ball, d.second_ball, d.third_ball, d.fourth_ball, d.fifth_ball] if b is not None]
        for i in range(len(balls)):
            for j in range(i + 1, len(balls)):
                cooc[balls[i]][balls[j]] += 1
                cooc[balls[j]][balls[i]] += 1

    ww = _white_weights(drawings)
    pw = _pb_weights(drawings)

    def generate():
        picked = [_weighted_sample(ww)]
        for _ in range(4):
            scores = {
                n: max(sum(cooc[p].get(n, 0) for p in picked), 0.1)
                for n in range(1, 70) if n not in picked
            }
            picked.append(_weighted_sample(scores))
        return sorted(picked), _weighted_sample(pw)

    generate.__name__ = "hot_pairs"
    return generate


def make_gap_theory(drawings):
    """#6 — weight each number by how long it's been since its last appearance."""
    now = datetime.now()
    last_seen_white = {}
    last_seen_pb = {}
    for d in drawings:
        if d.date_drawn is None:
            continue
        for ball in [d.first_ball, d.second_ball, d.third_ball, d.fourth_ball, d.fifth_ball]:
            if ball is not None and (ball not in last_seen_white or d.date_drawn > last_seen_white[ball]):
                last_seen_white[ball] = d.date_drawn
        if d.power_ball is not None and (
            d.power_ball not in last_seen_pb or d.date_drawn > last_seen_pb[d.power_ball]
        ):
            last_seen_pb[d.power_ball] = d.date_drawn

    never_weight = 365 * 5
    ww = _fill_white(_freq_to_weights({
        n: (now - last_seen_white[n]).days + 1 if n in last_seen_white else never_weight
        for n in range(1, 70)
    }))
    pw = _fill_pb(_freq_to_weights({
        n: (now - last_seen_pb[n]).days + 1 if n in last_seen_pb else never_weight
        for n in range(1, 27)
    }))

    def generate():
        return _pick_five(ww), _weighted_sample(pw)

    generate.__name__ = "gap_theory"
    return generate


def make_winning_ticket(drawings):
    """#7 — frequency table built only from drawings where winner = True."""
    winners = [d for d in drawings if d.winner is True]
    source = winners if winners else drawings
    ww = _white_weights(source)
    pw = _pb_weights(source)

    def generate():
        return _pick_five(ww), _weighted_sample(pw)

    generate.__name__ = "winning_ticket"
    return generate


def make_calendar_conditioned(drawings):
    """#8 — frequency table from draws that happened on today's day-of-week."""
    today_dow = datetime.now().weekday()
    subset = [d for d in drawings if d.day_of_week == today_dow]
    if not subset:
        subset = [d for d in drawings if d.date_drawn and d.date_drawn.month == datetime.now().month]
    if not subset:
        subset = drawings
    ww = _white_weights(subset)
    pw = _pb_weights(subset)

    def generate():
        return _pick_five(ww), _weighted_sample(pw)

    generate.__name__ = "calendar_conditioned"
    return generate


def make_state_conditioned(drawings):
    """#9 — frequency table from winning draws in a randomly selected state."""
    winners = [d for d in drawings if d.winner is True and d.winner_state]
    if winners:
        state_counts = defaultdict(int)
        for d in winners:
            state_counts[d.winner_state] += 1
        state = _weighted_sample(dict(state_counts))
        source = [d for d in winners if d.winner_state == state]
    else:
        state = None
        source = drawings
    ww = _white_weights(source)
    pw = _pb_weights(source)

    def generate():
        return _pick_five(ww), _weighted_sample(pw)

    generate.__name__ = f"state_conditioned_{state or 'all'}"
    return generate



def make_drought_breaker(drawings):
    """#12 — shifts weighting based on whether the current win-gap exceeds historical average."""
    now = datetime.now()
    win_dates = sorted(d.date_drawn for d in drawings if d.winner is True and d.date_drawn)

    if not win_dates:
        return make_hot_numbers(drawings)

    last_win = win_dates[-1]
    days_since = (now - last_win).days
    gaps = [(win_dates[i + 1] - win_dates[i]).days for i in range(len(win_dates) - 1)]
    mean_gap = statistics.mean(gaps) if gaps else 0

    if days_since > mean_gap and gaps:
        # Use the winning draws that ended droughts longer than average
        drought_enders = []
        for i in range(1, len(win_dates)):
            if (win_dates[i] - win_dates[i - 1]).days > mean_gap:
                for d in drawings:
                    if d.date_drawn == win_dates[i] and d.winner is True:
                        drought_enders.append(d)
                        break
        source = drought_enders if drought_enders else [d for d in drawings if d.winner is True]
    else:
        cutoff = now - timedelta(days=TRAILING_DAYS)
        source = [d for d in drawings if d.date_drawn and d.date_drawn >= cutoff] or drawings

    ww = _white_weights(source)
    pw = _pb_weights(source)

    def generate():
        return _pick_five(ww), _weighted_sample(pw)

    generate.__name__ = "drought_breaker"
    return generate


def make_ensemble_voting(sub_generators, runs_per_algo=5):
    """#13 — tallies votes from multiple algorithms; picks the most-voted numbers."""
    def generate():
        white_votes = defaultdict(int)
        pb_votes = defaultdict(int)
        for gen in sub_generators:
            for _ in range(runs_per_algo):
                white, pb = gen()
                for n in white:
                    white_votes[n] += 1
                pb_votes[pb] += 1
        top_white = sorted(sorted(white_votes, key=lambda n: -white_votes[n])[:5])
        top_pb = max(pb_votes, key=lambda n: pb_votes[n])
        return top_white, top_pb

    generate.__name__ = "ensemble_voting"
    return generate


def make_pure_chaos(_drawings):
    """#14 — true uniform random, no history."""
    def generate():
        return sorted(random.sample(range(1, 70), 5)), random.randint(1, 26)

    generate.__name__ = "pure_chaos"
    return generate


# ── Registry ──────────────────────────────────────────────────────────────────

def build_registry(drawings):
    hot = make_hot_numbers(drawings)
    cold = make_cold_numbers(drawings)
    pos = make_position_specific(drawings)
    markov = make_markov_chain(drawings)
    pairs = make_hot_pairs(drawings)
    gap = make_gap_theory(drawings)
    winner = make_winning_ticket(drawings)
    calendar = make_calendar_conditioned(drawings)
    state = make_state_conditioned(drawings)
    drought = make_drought_breaker(drawings)
    chaos = make_pure_chaos(drawings)
    ensemble = make_ensemble_voting([hot, cold, pos, markov, pairs, gap, winner, calendar, state, drought, chaos])

    return [hot, cold, pos, markov, pairs, gap, winner, calendar, state,
            drought, ensemble, chaos]
