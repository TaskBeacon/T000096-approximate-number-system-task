from __future__ import annotations

import hashlib
import random
from statistics import mean
from typing import Any


RATIO_PAIRS: dict[str, tuple[tuple[int, int], ...]] = {
    "1:2": ((5, 10), (6, 12), (7, 14), (8, 16)),
    "3:4": ((6, 8), (9, 12), (12, 16)),
    "5:6": ((5, 6), (10, 12)),
    "7:8": ((7, 8), (14, 16)),
}
MORE_COLORS = ("blue", "yellow")
VISUAL_CONTROLS = ("equal_average_size", "equal_total_area")


class ANSTrialPlan(str):
    def __new__(
        cls,
        *,
        condition_id: str,
        ratio: str,
        blue_count: int,
        yellow_count: int,
        more_color: str,
        visual_control: str,
        is_practice: bool,
        correct_key: str,
        stimulus_seed: int,
        trial_index_in_block: int,
    ) -> "ANSTrialPlan":
        obj = str.__new__(cls, condition_id)
        obj.condition_id = str(condition_id)
        obj.ratio = str(ratio)
        obj.blue_count = int(blue_count)
        obj.yellow_count = int(yellow_count)
        obj.more_color = str(more_color)
        obj.visual_control = str(visual_control)
        obj.is_practice = bool(is_practice)
        obj.correct_key = str(correct_key)
        obj.stimulus_seed = int(stimulus_seed)
        obj.trial_index_in_block = int(trial_index_in_block)
        return obj

    def to_dict(self) -> dict[str, Any]:
        smaller = min(self.blue_count, self.yellow_count)
        larger = max(self.blue_count, self.yellow_count)
        return {
            "condition_id": self.condition_id,
            "ratio": self.ratio,
            "ratio_value": larger / smaller,
            "blue_count": self.blue_count,
            "yellow_count": self.yellow_count,
            "more_color": self.more_color,
            "visual_control": self.visual_control,
            "is_practice": self.is_practice,
            "correct_key": self.correct_key,
            "stimulus_seed": self.stimulus_seed,
            "trial_index_in_block": self.trial_index_in_block,
        }


def _stable_seed(base_seed: int, *parts: object) -> int:
    payload = "|".join([str(base_seed), *(str(part) for part in parts)])
    digest = hashlib.blake2b(payload.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big")


def _make_plan(
    *,
    ratio: str,
    more_color: str,
    visual_control: str,
    pair_index: int,
    is_practice: bool,
    color_keys: dict[str, str],
    seed: int,
    block_index: int,
    trial_index: int,
) -> ANSTrialPlan:
    smaller, larger = RATIO_PAIRS[ratio][pair_index % len(RATIO_PAIRS[ratio])]
    blue_count, yellow_count = (
        (larger, smaller) if more_color == "blue" else (smaller, larger)
    )
    kind = "practice" if is_practice else "test"
    condition_id = (
        f"{kind}_ratio_{ratio.replace(':', '_')}_{more_color}_"
        f"{visual_control}_{blue_count}b_{yellow_count}y"
    )
    return ANSTrialPlan(
        condition_id=condition_id,
        ratio=ratio,
        blue_count=blue_count,
        yellow_count=yellow_count,
        more_color=more_color,
        visual_control=visual_control,
        is_practice=is_practice,
        correct_key=str(color_keys[more_color]),
        stimulus_seed=_stable_seed(seed, block_index, kind, trial_index, condition_id),
        trial_index_in_block=trial_index,
    )


def _practice_records(count: int, block_index: int) -> list[tuple[str, str, str]]:
    ratios = list(RATIO_PAIRS)
    combos = [
        ("blue", "equal_average_size"),
        ("yellow", "equal_total_area"),
        ("blue", "equal_total_area"),
        ("yellow", "equal_average_size"),
    ]
    return [
        (
            ratios[(index + 2 * block_index) % len(ratios)],
            *combos[(index + block_index) % len(combos)],
        )
        for index in range(count)
    ]


def _test_records(count: int, block_index: int) -> list[tuple[str, str, str]]:
    if count % 4:
        raise ValueError("test_trials_per_block must be divisible by four ratios")
    per_ratio = count // 4
    cells = [
        ("blue", "equal_average_size"),
        ("blue", "equal_total_area"),
        ("yellow", "equal_average_size"),
        ("yellow", "equal_total_area"),
    ]
    records: list[tuple[str, str, str]] = []
    for ratio in RATIO_PAIRS:
        base, remainder = divmod(per_ratio, len(cells))
        counts = [base] * len(cells)
        if remainder == 2:
            extras = (0, 3) if block_index % 2 == 0 else (1, 2)
        else:
            extras = tuple((block_index + offset) % len(cells) for offset in range(remainder))
        for cell_index in extras:
            counts[cell_index] += 1
        for (more_color, visual_control), repeats in zip(cells, counts):
            records.extend((ratio, more_color, visual_control) for _ in range(repeats))
    return records


def generate_session_plans(
    *,
    total_blocks: int,
    practice_trials_per_block: int,
    test_trials_per_block: int,
    color_keys: dict[str, str],
    seed: int,
) -> list[list[ANSTrialPlan]]:
    blocks: list[list[ANSTrialPlan]] = []
    pair_counters = {ratio: 0 for ratio in RATIO_PAIRS}
    for block_index in range(int(total_blocks)):
        practice_records = _practice_records(int(practice_trials_per_block), block_index)
        test_records = _test_records(int(test_trials_per_block), block_index)
        rng = random.Random(_stable_seed(seed, "block", block_index))
        rng.shuffle(practice_records)
        rng.shuffle(test_records)
        records = [(record, True) for record in practice_records] + [
            (record, False) for record in test_records
        ]
        plans: list[ANSTrialPlan] = []
        for trial_index, ((ratio, more_color, visual_control), is_practice) in enumerate(records):
            pair_index = pair_counters[ratio]
            pair_counters[ratio] += 1
            plans.append(
                _make_plan(
                    ratio=ratio,
                    more_color=more_color,
                    visual_control=visual_control,
                    pair_index=pair_index,
                    is_practice=is_practice,
                    color_keys=color_keys,
                    seed=seed,
                    block_index=block_index,
                    trial_index=trial_index,
                )
            )
        blocks.append(plans)
    return blocks


def summarize_trials(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scored = [row for row in rows if not bool(row.get("is_practice"))]
    answered = [row for row in scored if row.get("response_key")]
    correct = [row for row in scored if bool(row.get("correct"))]
    correct_rts = [
        float(row["response_rt"])
        for row in correct
        if isinstance(row.get("response_rt"), (int, float))
    ]
    ratio_accuracy = {
        ratio: (
            sum(bool(row.get("correct")) for row in scored if row.get("ratio") == ratio)
            / max(1, sum(row.get("ratio") == ratio for row in scored))
        )
        for ratio in RATIO_PAIRS
    }
    return {
        "trials": len(scored),
        "response_rate": len(answered) / len(scored) if scored else 0.0,
        "accuracy": len(correct) / len(scored) if scored else 0.0,
        "mean_rt": mean(correct_rts) if correct_rts else None,
        "omissions": len(scored) - len(answered),
        "ratio_accuracy": ratio_accuracy,
    }
