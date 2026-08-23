from __future__ import annotations

from typing import Any

from psyflow import StimUnit, next_trial_id, set_trial_context

from .utils import ANSTrialPlan


def _context(
    unit: StimUnit,
    *,
    trial_id: int,
    block_id: str,
    plan: ANSTrialPlan,
    phase: str,
    deadline: float,
    keys: list[str],
    stim_id: str,
    extra_factors: dict[str, Any] | None = None,
) -> None:
    factors = {**plan.to_dict(), "stage": phase}
    if extra_factors:
        factors.update(extra_factors)
    set_trial_context(
        unit,
        trial_id=trial_id,
        phase=phase,
        deadline_s=float(deadline),
        valid_keys=list(keys),
        block_id=block_id,
        condition_id=plan.condition_id,
        task_factors=factors,
        stim_id=stim_id,
    )


def _dot_trigger_name(plan: ANSTrialPlan) -> str:
    control = "size" if plan.visual_control == "equal_average_size" else "area"
    return f"dots_{plan.ratio.replace(':', '_')}_{plan.more_color}_{control}"


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    trigger_runtime,
    block_id=None,
    block_idx=None,
):
    if not isinstance(condition, ANSTrialPlan):
        raise TypeError("Approximate Number System trials require a preplanned ANSTrialPlan")
    plan = condition
    trial_id = int(next_trial_id())
    block_name = str(block_id or f"block_{int(block_idx or 0) + 1}")
    color_keys = {str(k): str(v) for k, v in dict(settings.color_keys).items()}
    response_keys = [color_keys["yellow"], color_keys["blue"]]
    response_triggers = {
        color_keys["yellow"]: settings.triggers.get("yellow_response"),
        color_keys["blue"]: settings.triggers.get("blue_response"),
    }
    data: dict[str, Any] = {
        "trial_id": trial_id,
        "block_id": block_name,
        "block_idx": int(block_idx or 0),
        **plan.to_dict(),
    }

    fixation_duration = float(settings.fixation_duration)
    fixation = StimUnit("fixation", win, kb, runtime=trigger_runtime).add_stim(
        stim_bank.get("fixation")
    )
    _context(
        fixation,
        trial_id=trial_id,
        block_id=block_name,
        plan=plan,
        phase="fixation",
        deadline=fixation_duration,
        keys=[],
        stim_id="fixation",
    )
    fixation.show(
        duration=fixation_duration,
        onset_trigger=settings.triggers.get("fixation"),
    ).to_dict(data)

    dot_duration = float(settings.dot_duration)
    dot_stim = stim_bank.rebuild(
        "intermixed_dot_array",
        blue_count=plan.blue_count,
        yellow_count=plan.yellow_count,
        visual_control=plan.visual_control,
        seed=plan.stimulus_seed,
    )
    comparison = StimUnit(
        "dot_comparison", win, kb, runtime=trigger_runtime
    ).add_stim(dot_stim)
    _context(
        comparison,
        trial_id=trial_id,
        block_id=block_name,
        plan=plan,
        phase="dot_comparison",
        deadline=dot_duration,
        keys=response_keys,
        stim_id="intermixed_dot_array",
    )
    comparison.capture_response(
        keys=response_keys,
        correct_keys=[plan.correct_key],
        duration=dot_duration,
        onset_trigger=settings.triggers.get(_dot_trigger_name(plan)),
        response_trigger=response_triggers,
        terminate_on_response=False,
    ).to_dict(data)
    response = comparison.get_state("response", None)
    response_rt = comparison.get_state("rt", None)

    if response is None:
        remaining = max(0.0, float(settings.response_window) - dot_duration)
        post_display = StimUnit(
            "post_display_response", win, kb, runtime=trigger_runtime
        ).add_stim(stim_bank.get("blank"))
        _context(
            post_display,
            trial_id=trial_id,
            block_id=block_name,
            plan=plan,
            phase="post_display_response",
            deadline=remaining,
            keys=response_keys,
            stim_id="blank_response_window",
        )
        post_display.capture_response(
            keys=response_keys,
            correct_keys=[plan.correct_key],
            duration=remaining,
            onset_trigger=settings.triggers.get("post_display_response"),
            response_trigger=response_triggers,
            timeout_trigger=settings.triggers.get("response_timeout"),
            terminate_on_response=True,
        ).to_dict(data)
        response = post_display.get_state("response", None)
        late_rt = post_display.get_state("rt", None)
        response_rt = (
            dot_duration + float(late_rt)
            if isinstance(late_rt, (int, float))
            else None
        )

    correct = response == plan.correct_key if response is not None else False
    outcome = "correct" if correct else "incorrect" if response is not None else "timeout"
    if plan.is_practice:
        feedback_duration = float(settings.practice_feedback_duration)
        if outcome == "correct":
            feedback_id = "practice_correct"
            feedback_stim = stim_bank.get(feedback_id)
            feedback_trigger = settings.triggers.get("practice_correct")
        elif outcome == "incorrect":
            feedback_id = "practice_incorrect"
            color_labels = dict(settings.color_labels)
            feedback_stim = stim_bank.get_and_format(
                feedback_id,
                correct_color=str(color_labels[plan.more_color]),
            )
            feedback_trigger = settings.triggers.get("practice_incorrect")
        else:
            feedback_id = "practice_timeout"
            feedback_stim = stim_bank.get(feedback_id)
            feedback_trigger = settings.triggers.get("response_timeout")
        feedback = StimUnit(
            "practice_feedback", win, kb, runtime=trigger_runtime
        ).add_stim(feedback_stim)
        _context(
            feedback,
            trial_id=trial_id,
            block_id=block_name,
            plan=plan,
            phase="practice_feedback",
            deadline=feedback_duration,
            keys=[],
            stim_id=feedback_id,
            extra_factors={"outcome": outcome},
        )
        feedback.show(
            duration=feedback_duration,
            onset_trigger=feedback_trigger,
        ).to_dict(data)

    data.update(
        response_key=str(response or ""),
        response_color=(
            "yellow" if response == color_keys["yellow"] else "blue" if response == color_keys["blue"] else ""
        ),
        response_rt=response_rt,
        correct=correct,
        timed_out=response is None,
        outcome=outcome,
    )

    iti_duration = float(settings.iti_duration)
    iti = StimUnit("iti", win, kb, runtime=trigger_runtime).add_stim(
        stim_bank.get("blank")
    )
    _context(
        iti,
        trial_id=trial_id,
        block_id=block_name,
        plan=plan,
        phase="iti",
        deadline=iti_duration,
        keys=[],
        stim_id="blank",
    )
    iti.show(
        duration=iti_duration,
        onset_trigger=settings.triggers.get("iti"),
    ).to_dict(data)
    return data
