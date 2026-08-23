# Stimulus Mapping

## Mapping Table

| Condition | Stage/Phase | Stimulus IDs | Participant-Facing Content | Source Paper ID | Evidence (quote/figure/table) | Implementation Mode | Asset References | Notes |
|---|---|---|---|---|---|---|---|---|
| `ratio_1_2` | dot comparison | `intermixed_dot_array` | Intermixed blue/yellow dots at 1:2 ratio, 5–16 dots per set | W2014481741 | Main text lists 1:2 and the 5–16 range. | `psychopy_builtin` | none | More color and control mode are balanced. |
| `ratio_3_4` | dot comparison | `intermixed_dot_array` | Intermixed blue/yellow dots at 3:4 ratio | W2014481741 | Main text lists 3:4. | `psychopy_builtin` | none | Exact pairs remain within 5–16. |
| `ratio_5_6` | dot comparison | `intermixed_dot_array` | Intermixed blue/yellow dots at 5:6 ratio | W2014481741 | Main text lists 5:6. | `psychopy_builtin` | none | Exact pairs remain within 5–16. |
| `ratio_7_8` | dot comparison | `intermixed_dot_array` | Intermixed blue/yellow dots at 7:8 ratio | W2014481741 | Main text lists 7:8. | `psychopy_builtin` | none | Exact pairs remain within 5–16. |
| `equal_average_size` | dot comparison | `intermixed_dot_array` | Both colors have equal dot diameter; the more numerous color has greater cumulative area | W2014481741; W639002133 | Half the primary trials were area-controlled; DeWind et al. identifies item size and total area as relevant features. | `psychopy_builtin` | none | Complementary congruent visual condition. |
| `equal_total_area` | dot comparison | `intermixed_dot_array` | More numerous color uses smaller dots so cumulative blue and yellow area is equal | W2014481741; W639002133 | Half the primary trials were area-controlled to prevent total area from determining the answer. | `psychopy_builtin` | none | Per-color diameter is computed from count. |
| all | fixation | `fixation` | White `+` centered on gray | W2014481741 | Orienting interval is not specified. | `psychopy_builtin` | none | Inferred 500 ms pre-display fixation. |
| all unanswered | post-display response | `blank` | Blank gray field while response remains available | W2014481741; W1967654316 | Dots are visible for 200 ms; 4 s is the supported RT boundary. | `psychopy_builtin` | none | Prevents counting after stimulus offset. |
| practice correct | practice feedback | `practice_correct` | Green Chinese text meaning "correct" | W2014481741 | Ten practice trials per session are reported; feedback details are unspecified. | `psychopy_builtin` | none | Inferred and practice-only. |
| practice incorrect | practice feedback | `practice_incorrect` | Orange Chinese text meaning "incorrect; correct color was ..." | W2014481741 | Ten practice trials per session are reported; feedback details are unspecified. | `psychopy_builtin` | none | Color name is config-formatted. |
| practice timeout | practice feedback | `practice_timeout` | Yellow Chinese text asking for a response within 4 seconds | W1967654316 | RT over 4 s was excluded. | `psychopy_builtin` | none | Explicit practice timeout message. |
