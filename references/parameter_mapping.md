# Parameter Mapping

## Mapping Table

| Parameter ID | Config Path | Implemented Value | Source Paper ID | Evidence (quote/figure/table) | Decision Type | Notes |
|---|---|---|---|---|---|---|
| task structure | `task.total_blocks`, `task.practice_trials_per_block`, `task.test_trials_per_block` | 2 blocks; 10 practice + 40 test per block | W2014481741 | Main text reports two sessions, each with 10 practice and 40 test trials, totaling 80 test trials. | direct | Implemented as two computerized blocks. |
| ratio set | `task.ratios` | `1:2`, `3:4`, `5:6`, `7:8` | W2014481741 | Main text lists the four randomly varying ratios. | direct | Each ratio has 20 test trials over the session. |
| numerosity range | `task.numerosity_range` | 5–16 dots per color | W2014481741 | Main text states between 5 and 16 dots in each set. | direct | Exact integer pairs preserve each canonical ratio. |
| more-color balance | generated `more_color` | blue/yellow balanced | W2014481741 | Main text states that the color of the more numerous set varied randomly. | adapted | Seeded balancing replaces unconstrained random imbalance. |
| visual control | generated `visual_control` | equal average size / equal total area, 50/50 | W2014481741; W639002133 | Main text states half the trials were area-controlled; DeWind et al. details bias from non-numerical visual features. | adapted | Equal-average-size trials provide the complementary congruent condition. |
| dot duration | `timing.dot_duration` | 0.200 s | W2014481741; W1967654316 | Both protocols specify a 200 ms intermixed blue/yellow dot display. | direct | Fixed across modes before QA scaling. |
| response deadline | `timing.response_window` | 4.000 s total | W1967654316 | Methods exclude individual trials with RT longer than 4 s. | adapted | Implemented as an explicit deadline rather than a post-hoc exclusion. |
| fixation | `timing.fixation_duration` | 0.500 s | W2014481741 | Not specified around the critical display. | inferred | Conservative task-typical orienting interval. |
| ITI | `timing.iti_duration` | 0.500 s | W2014481741 | Not specified. | inferred | Stable brief separation without feedback on test trials. |
| practice feedback | `timing.practice_feedback_duration` | 0.500 s | W2014481741 | Practice trials are reported but feedback duration is not. | inferred | Only practice receives correctness feedback. |
| response keys | `task.color_keys` | yellow=`f`, blue=`j` | W2014481741 | Responses were made by key press and verbal response; exact keys are not specified. | inferred | Config-defined and taught in Chinese instructions. |
| dot layout | `task.aperture_radius_deg`, `task.dot_diameter_deg`, `task.min_gap_deg` | 7.0°, 0.65°, 0.10° | W2014481741; W639002133 | Sources require brief intermixed dots and control of non-numerical features but do not prescribe monitor-specific geometry. | inferred | Deterministic non-overlap packing preserves legibility. |
| seed | `task.plan_seed` | 96096 | W639002133 | Reproducible visual feature specification is necessary for audit. | inferred | Separates condition planning from stimulus-position realization. |
