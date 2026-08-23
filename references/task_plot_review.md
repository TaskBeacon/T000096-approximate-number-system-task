# Task Plot Review

## Round 1

- Evidence match: phase order, labels, timings, blank post-display response screen, ITI, key note, and practice-only feedback note are correct.
- Visual quality: clean landscape layout, readable text, no overlaps, fixed title/subtitle/logo lockup correct.
- Failed gate: DOTS panels do not preserve every requested blue/yellow count. The `1:2` panel is visibly not 10 blue vs 5 yellow, and the controlled-area rows also need exact count verification.
- Revision request: keep the layout and wording; replace only DOTS panel contents with exact per-row counts, and preserve smaller dots for the more-numerous color in equal-total-area rows.

## Round 2

- Evidence match: phase order, labels, timings, blank response/ITI screens, and condition names remain correct.
- Visual quality: rows are readable and well separated.
- Failed gate 1: first row contains 9 blue and 6 yellow dots instead of 10 blue and 5 yellow.
- Failed gate 2: second row contains 6 blue and 7 yellow dots instead of 6 blue and 8 yellow.
- Failed gate 3: the raw header-safe area is too shallow, causing the fixed construct subtitle to overlap the first row's phase labels.
- Revision request: edit only the first two DOTS panels and shift timeline content below a clean 18% white header band.

## Round 3

- Passed header/layout gate: fixed subtitle no longer overlaps phase labels and all four rows remain visible.
- Failed count gate: first row has 9 blue + 5 yellow; second row has 7 blue + 8 yellow.
- Revision request: add one blue to row 1 and remove one blue from row 2 only.

## Round 4

- Passed layout/text gate and second-row blue-count correction.
- Failed count gate: first row remains 9 blue + 5 yellow; second row changed to 6 blue + 6 yellow because two yellow dots were unintentionally removed.
- Revision request: replace all four DOTS panels with explicitly enumerated, lightly jittered interleaved grids so every count is directly auditable.

## Round 5

- Passed: fixed header/title/subtitle/logo, row layout, phase order, phase labels, timings, notes, readability, and no overlap.
- Passed count: row 1 is exactly 10 blue + 5 yellow; row 2 is exactly 6 blue + 8 yellow.
- Failed scale gate: row 2 contains one blue dot smaller than the other blue dots, contradicting the per-color diameter control.
- Failed count/scale gate: row 4 contains an extra blue dot and does not preserve the exact equal-size 7 blue + 8 yellow display.
- Final status: `fail_after_5_rounds`. The plot is not approved for README embedding or publication.
- Pipeline consequence: do not start `task-py2js`, do not mark the task complete, and do not publish until the user authorizes additional plot iterations or a new compliant plotting strategy.

## Round 6

- User authorized additional `task-plot` iterations after the original five-round cap.
- Targeted corrections: normalize the one undersized blue dot in row 2; remove the extra rightmost blue dot in row 4; normalize the one undersized yellow dot in row 4.
- Passed header/layout/text/timing gates and preserved rows 1-3.
- Passed row-2 count/scale gate: exactly 6 blue + 8 yellow, with the blue set consistently larger for the equal-total-area example.
- Failed row-4 count gate: the edited panel contains 8 blue + 7 yellow instead of 7 blue + 8 yellow.
- Revision request: recolor only the bottom-right blue dot in row 4 to yellow, preserving its size and position.

## Round 7

- Targeted correction: recolor only the bottom-right dot in row 4 from blue to yellow.
- Passed count gate: row 4 now contains exactly 7 blue + 8 yellow dots, all at the same diameter.
- Passed full visual gate: all four examples preserve the intended ratios and size/area controls; phase order, timings, response mapping, typography, spacing, and watermark are correct and unobstructed.
- Final status: `pass`.
