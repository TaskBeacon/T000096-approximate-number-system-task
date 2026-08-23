from collections import Counter

from src.utils import RATIO_PAIRS, generate_session_plans


def test_primary_protocol_plan_is_balanced_and_reproducible():
    kwargs = dict(
        total_blocks=2,
        practice_trials_per_block=10,
        test_trials_per_block=40,
        color_keys={"yellow": "f", "blue": "j"},
        seed=96096,
    )
    first = generate_session_plans(**kwargs)
    second = generate_session_plans(**kwargs)
    assert [[plan.to_dict() for plan in block] for block in first] == [
        [plan.to_dict() for plan in block] for block in second
    ]
    assert [len(block) for block in first] == [50, 50]

    tests = [plan for block in first for plan in block if not plan.is_practice]
    assert len(tests) == 80
    assert Counter(plan.ratio for plan in tests) == {ratio: 20 for ratio in RATIO_PAIRS}
    assert Counter(plan.more_color for plan in tests) == {"blue": 40, "yellow": 40}
    assert Counter(plan.visual_control for plan in tests) == {
        "equal_average_size": 40,
        "equal_total_area": 40,
    }
    cells = Counter((plan.ratio, plan.more_color, plan.visual_control) for plan in tests)
    assert set(cells.values()) == {5}


def test_counts_keys_and_range_match_each_plan():
    blocks = generate_session_plans(
        total_blocks=2,
        practice_trials_per_block=4,
        test_trials_per_block=8,
        color_keys={"yellow": "f", "blue": "j"},
        seed=96096,
    )
    for plan in [plan for block in blocks for plan in block]:
        assert 5 <= plan.blue_count <= 16
        assert 5 <= plan.yellow_count <= 16
        assert plan.correct_key == ("j" if plan.blue_count > plan.yellow_count else "f")
        smaller, larger = sorted((plan.blue_count, plan.yellow_count))
        assert (smaller, larger) in RATIO_PAIRS[plan.ratio]
