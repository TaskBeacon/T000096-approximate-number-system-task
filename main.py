from __future__ import annotations

from contextlib import nullcontext
from functools import partial
from pathlib import Path
from typing import Any

import pandas as pd
from psychopy import core
from psyflow import (
    BlockUnit,
    StimBank,
    StimUnit,
    SubInfo,
    TaskRunOptions,
    TaskSettings,
    context_from_config,
    count_down,
    initialize_exp,
    initialize_triggers,
    load_config,
    parse_task_run_options,
    reset_trial_counter,
    runtime_context,
)

from src import generate_session_plans, register_dot_array_stimulus, run_trial, summarize_trials


MODES = ("human", "qa", "sim")
DEFAULT_CONFIG_BY_MODE = {
    "human": "config/config.yaml",
    "qa": "config/config_qa.yaml",
    "sim": "config/config_scripted_sim.yaml",
}


def _format_rt(value: float | None) -> str:
    return "--" if value is None else f"{value * 1000.0:.0f} ms"


def _execute_block(
    *,
    block_id: str,
    block_idx: int,
    plans: list[Any],
    settings: TaskSettings,
    win: Any,
    kb: Any,
    stim_bank: StimBank,
    trigger_runtime: Any,
    sink: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    block = (
        BlockUnit(
            block_id=block_id,
            block_idx=block_idx,
            settings=settings,
            window=win,
            keyboard=kb,
        )
        .add_condition(plans)
        .on_start(lambda _: trigger_runtime.send(settings.triggers.get("block_start")))
        .on_end(lambda _: trigger_runtime.send(settings.triggers.get("block_end")))
        .run_trial(
            partial(
                run_trial,
                stim_bank=stim_bank,
                trigger_runtime=trigger_runtime,
                block_id=block_id,
                block_idx=block_idx,
            )
        )
        .to_dict(sink)
    )
    return list(block.get_all_data())


def run(options: TaskRunOptions) -> None:
    task_root = Path(__file__).resolve().parent
    config = load_config(str(options.config_path))
    output_dir: Path | None = None
    scope = nullcontext()
    runtime_ctx = None
    if options.mode in ("qa", "sim"):
        runtime_ctx = context_from_config(task_dir=task_root, config=config, mode=options.mode)
        output_dir = runtime_ctx.output_dir
        scope = runtime_context(runtime_ctx)

    with scope:
        if options.mode == "qa":
            subject = {"subject_id": "qa"}
        elif options.mode == "sim":
            subject = {
                "subject_id": str(runtime_ctx.session.participant_id or "sim")
                if runtime_ctx
                else "sim"
            }
        else:
            subject = SubInfo(config["subform_config"]).collect()

        settings = TaskSettings.from_dict(config["task_config"])
        settings.add_subinfo(subject)
        if output_dir is not None:
            settings.save_path = str(output_dir)
        if options.mode == "qa" and output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            settings.res_file = str(output_dir / "qa_trace.csv")
            settings.log_file = str(output_dir / "qa_psychopy.log")
            settings.json_file = str(output_dir / "qa_settings.json")

        settings.triggers = config["trigger_config"]
        triggers = (
            initialize_triggers(mock=True)
            if options.mode in ("qa", "sim")
            else initialize_triggers(config)
        )
        win, kb = initialize_exp(settings)
        bank = StimBank(win, config["stim_config"])
        register_dot_array_stimulus(bank, settings)
        bank.preload_all()
        settings.save_to_json()
        reset_trial_counter()
        triggers.send(settings.triggers.get("experiment_start"))

        StimUnit("instruction", win, kb, runtime=triggers).add_stim(
            bank.get("instruction")
        ).wait_and_continue()

        blocks = generate_session_plans(
            total_blocks=int(settings.total_blocks),
            practice_trials_per_block=int(settings.practice_trials_per_block),
            test_trials_per_block=int(settings.test_trials_per_block),
            color_keys={str(k): str(v) for k, v in dict(settings.color_keys).items()},
            seed=int(settings.plan_seed),
        )
        all_rows: list[dict[str, Any]] = []
        for block_idx, plans in enumerate(blocks):
            StimUnit("block_instruction", win, kb, runtime=triggers).add_stim(
                bank.get_and_format(
                    "block_instruction",
                    block_number=block_idx + 1,
                    total_blocks=len(blocks),
                    practice_trials=int(settings.practice_trials_per_block),
                    test_trials=int(settings.test_trials_per_block),
                )
            ).wait_and_continue()
            if options.mode == "human":
                count_down(win, 3, color="white")
            block_rows = _execute_block(
                block_id=f"block_{block_idx + 1}",
                block_idx=block_idx,
                plans=plans,
                settings=settings,
                win=win,
                kb=kb,
                stim_bank=bank,
                trigger_runtime=triggers,
                sink=all_rows,
            )
            if block_idx < len(blocks) - 1:
                summary = summarize_trials(block_rows)
                StimUnit("block_break", win, kb, runtime=triggers).add_stim(
                    bank.get_and_format(
                        "block_break",
                        block_number=block_idx + 1,
                        total_blocks=len(blocks),
                        accuracy=f"{summary['accuracy']:.1%}",
                        mean_rt=_format_rt(summary["mean_rt"]),
                    )
                ).wait_and_continue()

        summary = summarize_trials(all_rows)
        StimUnit("good_bye", win, kb, runtime=triggers).add_stim(
            bank.get_and_format(
                "good_bye",
                accuracy=f"{summary['accuracy']:.1%}",
                response_rate=f"{summary['response_rate']:.1%}",
                mean_rt=_format_rt(summary["mean_rt"]),
                easy_accuracy=f"{summary['ratio_accuracy']['1:2']:.1%}",
                hard_accuracy=f"{summary['ratio_accuracy']['7:8']:.1%}",
            )
        ).wait_and_continue(terminate=True)

        triggers.send(settings.triggers.get("experiment_end"))
        pd.DataFrame(all_rows).to_csv(settings.res_file, index=False)
        triggers.close()
        core.quit()


def main() -> None:
    run(
        parse_task_run_options(
            task_root=Path(__file__).resolve().parent,
            description="Run the Approximate Number System task.",
            default_config_by_mode=DEFAULT_CONFIG_BY_MODE,
            modes=MODES,
        )
    )


if __name__ == "__main__":
    main()
