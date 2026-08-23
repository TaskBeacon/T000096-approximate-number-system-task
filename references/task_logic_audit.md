# Task Logic Audit

This audit was extracted from the cited papers before task code was written. The primary protocol is Halberda, Mazzocco, and Feigenson (2008), with response-window and visual-control support from Halberda et al. (2012) and DeWind et al. (2015).

## 1. Paradigm Intent

- Task: Approximate Number System task (intermixed blue/yellow dot comparison).
- Primary construct: non-symbolic numerosity discrimination / ANS acuity.
- Manipulated factors: numerical ratio (`1:2`, `3:4`, `5:6`, `7:8`), more-numerous color (blue/yellow), and non-numerical visual control (equal average dot size/equal cumulative dot area).
- Dependent measures: accuracy and reaction time by ratio and visual-control mode; data are sufficient for a downstream Weber-fraction fit.
- Key citations: W2014481741 (primary), W1967654316 (replication and response-window support), W639002133 (visual-feature control).

## 2. Block/Trial Workflow

### Block Structure

- Total blocks: 2.
- Trials per block: 10 practice trials followed by 40 test trials; 20 practice and 80 test trials total, matching W2014481741.
- Randomization/counterbalancing: a seeded session plan balances the four ratios, more-numerous color, and visual-control mode across the 80 test trials. Every ratio × more-color × visual-control cell occurs five times across the session. Practice trials span all ratios and both response colors.
- Condition weight policy: not applicable because the literature requires balanced item-level numerosity pairs rather than simple repeated labels.
- Condition generation method: custom preplanned `ANSTrialPlan` objects are passed to `BlockUnit.add_condition(...)`. Simple labels are insufficient because exact dot counts, ratio, more-numerous color, visual-control mode, practice status, correct key, and stable stimulus seed must remain jointly balanced and auditable.
- Generated condition shape: string-compatible `ANSTrialPlan` with `condition_id`, ratio, blue/yellow counts, more color, visual-control mode, practice flag, correct key, and stimulus seed.
- Runtime-generated trial values: none of the experimental factors are randomized in `run_trial.py`; dot locations and sizes are deterministically realized by the registered dot-array stimulus from the preplanned counts, control mode, and seed.

### Trial State Machine

1. Fixation
   - Onset trigger: `fixation`.
   - Stimuli shown: central white `+` on gray.
   - Valid keys: none.
   - Timeout behavior: advances after 500 ms.
   - Next state: dot comparison.
2. Dot comparison
   - Onset trigger: ratio × more-color × visual-control trigger.
   - Stimuli shown: spatially intermixed blue and yellow dot sets for 200 ms.
   - Valid keys: `F` for yellow and `J` for blue.
   - Timeout behavior: if unanswered after the 200 ms display, continue accepting the same keys on a blank gray screen until the 4 s total response deadline.
   - Next state: practice feedback when the trial is practice; otherwise ITI.
3. Post-display response (conditional)
   - Onset trigger: `post_display_response`.
   - Stimuli shown: blank gray field so dots cannot be counted.
   - Valid keys: `F`, `J`.
   - Timeout behavior: record omission at the 4 s total deadline.
   - Next state: practice feedback when practice; otherwise ITI.
4. Practice feedback (practice only)
   - Onset trigger: `practice_correct`, `practice_incorrect`, or `response_timeout`.
   - Stimuli shown: Chinese correctness/timeout message.
   - Valid keys: none.
   - Timeout behavior: advances after 500 ms.
   - Next state: ITI.
5. ITI
   - Onset trigger: `iti`.
   - Stimuli shown: blank gray field.
   - Valid keys: none.
   - Timeout behavior: advances after 500 ms.
   - Next state: next trial or block summary.

## 3. Condition Semantics

- `ratio_1_2`: easy 1:2 comparison; count pairs are 5:10, 6:12, 7:14, or 8:16.
- `ratio_3_4`: intermediate 3:4 comparison; count pairs are 6:8, 9:12, or 12:16.
- `ratio_5_6`: difficult 5:6 comparison; count pairs are 5:6 or 10:12.
- `ratio_7_8`: hardest 7:8 comparison; count pairs are 7:8 or 14:16.
- More-color realization: the larger count is assigned to blue or yellow by the balanced plan; the correct key follows the configured color-key mapping.
- `equal_average_size`: all dots share the same diameter, so cumulative area is congruent with numerosity.
- `equal_total_area`: dot diameter is scaled by set size so blue and yellow cumulative areas are equal, preventing cumulative area from identifying the answer.
- Participant-facing text source: all instructions and feedback live in `config/*.yaml`; dot colors/sizes/aperture parameters are config-driven and materialized through a registered PsychoPy stimulus.
- Localization strategy: participant wording can be replaced in config without code edits.

## 4. Response and Scoring Rules

- Response mapping: `F` = yellow more numerous; `J` = blue more numerous.
- Response key source: `task.color_keys` in config.
- Missing-response policy: no response by 4 s is an omission/timeout and incorrect.
- Correctness logic: response key equals the preplanned key for the more-numerous color.
- Reward/penalty updates: none.
- Running metrics: test-trial response rate, accuracy, correct-trial mean RT, and ratio-specific accuracy; practice trials are excluded.

## 5. Stimulus Layout Plan

- Screen name: dot comparison.
- Stimulus IDs shown together: `intermixed_dot_array` containing both color sets.
- Layout anchors: both sets share a circular aperture centered at `[0, 0]`; positions are jointly sampled so colors spatially intermix.
- Size/spacing: 7-degree radius aperture; default diameter 0.65 degrees; minimum edge gap 0.10 degrees; the area-equal mode adjusts per-color diameter while preserving total area.
- Readability/overlap checks: deterministic rejection sampling prevents dot overlap; QA captures all ratios and both control modes; plot audit verifies relative dot numerosity and dot-size relation.
- Rationale: a shared aperture reproduces W2014481741's spatially intermixed blue/yellow display and removes left/right spatial choice cues.

## 6. Trigger Plan

- Experiment start/end: 1/99.
- Block start/end: 10/90.
- Fixation: 20.
- Dot display: 31–46 for ratio × more-color × control cells.
- Yellow/blue response: 51/52.
- Response timeout: 53.
- Post-display response window: 60.
- Practice correct/incorrect: 71/72.
- ITI: 80.

## 7. Architecture Decisions (Auditability)

- `main.py` runtime flow style: one explicit mode-aware flow with session-plan generation, practice/test block execution, summaries, and persistence.
- `utils.py` used: yes, only for balanced trial-plan generation and summary calculations that cannot be expressed by simple condition labels.
- Custom stimulus module used: yes, to realize non-overlapping intermixed dot arrays with controlled cumulative area through PsychoPy `ElementArrayStim`.
- Custom controller used: no; the task is non-adaptive.
- Legacy/backward-compatibility fallback logic required: no.

## 8. Inference Log

- Fixation duration of 500 ms and ITI of 500 ms are conservative task-typical values because W2014481741 specifies the critical 200 ms dot display but not those inter-phase intervals.
- A 4 s total response deadline is adapted from W1967654316, which excluded trials with RT above 4 s; this makes the exclusion boundary an explicit timeout.
- Practice feedback for 500 ms is inferred because W2014481741 reports practice trials without specifying feedback details; feedback is limited to practice and excluded from test trials.
- Blue/yellow key assignment uses `F/J` rather than the paper's unspecified physical keys; it is config-defined, counter-spatially neutral because the arrays are intermixed, and taught before the task.
- Dot aperture, default diameter, and minimum separation are inferred implementation geometry. They preserve the cited mixed-color, uncountable, non-overlapping display while remaining legible at the configured monitor geometry.

## Contract Note

- Participant-facing labels, instructions, options, and feedback are config-defined.
- `src/run_trial.py` contains only phase orchestration; no core trial factor is generated there.
