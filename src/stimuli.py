from __future__ import annotations

import math

import numpy as np
from psychopy import visual
from psychopy.visual.basevisual import BaseVisualStim


class IntermixedDotArrayStim(BaseVisualStim):
    """Static, deterministic, non-overlapping blue/yellow dot array."""

    def __init__(
        self,
        win,
        *,
        blue_count: int = 8,
        yellow_count: int = 6,
        visual_control: str = "equal_average_size",
        seed: int = 0,
        aperture_radius_deg: float = 7.0,
        dot_diameter_deg: float = 0.65,
        min_gap_deg: float = 0.10,
        blue_color: str = "#2196F3",
        yellow_color: str = "#FFEB3B",
    ):
        super().__init__(win, units="deg", name="intermixed_dot_array", autoLog=False)
        if visual_control not in {"equal_average_size", "equal_total_area"}:
            raise ValueError(f"Unsupported visual control: {visual_control}")
        self.rng = np.random.default_rng(int(seed))
        self.blue_count = int(blue_count)
        self.yellow_count = int(yellow_count)
        self.visual_control = str(visual_control)
        self.aperture_radius = float(aperture_radius_deg)
        self.min_gap = float(min_gap_deg)

        blue_diameter, yellow_diameter = self._diameters(float(dot_diameter_deg))
        labels = np.array(
            ["blue"] * self.blue_count + ["yellow"] * self.yellow_count,
            dtype=object,
        )
        diameters = np.array(
            [blue_diameter] * self.blue_count
            + [yellow_diameter] * self.yellow_count,
            dtype=float,
        )
        order = self.rng.permutation(len(labels))
        labels = labels[order]
        diameters = diameters[order]
        positions = self._sample_nonoverlapping(diameters)

        blue_mask = labels == "blue"
        yellow_mask = labels == "yellow"
        self.blue = visual.ElementArrayStim(
            win,
            nElements=int(np.count_nonzero(blue_mask)),
            xys=positions[blue_mask],
            sizes=np.column_stack((diameters[blue_mask], diameters[blue_mask])),
            colors=blue_color,
            elementTex=None,
            elementMask="circle",
            units="deg",
        )
        self.yellow = visual.ElementArrayStim(
            win,
            nElements=int(np.count_nonzero(yellow_mask)),
            xys=positions[yellow_mask],
            sizes=np.column_stack((diameters[yellow_mask], diameters[yellow_mask])),
            colors=yellow_color,
            elementTex=None,
            elementMask="circle",
            units="deg",
        )

    def _diameters(self, base_diameter: float) -> tuple[float, float]:
        if self.visual_control == "equal_average_size":
            return base_diameter, base_diameter
        reference_count = math.sqrt(self.blue_count * self.yellow_count)
        return (
            base_diameter * math.sqrt(reference_count / self.blue_count),
            base_diameter * math.sqrt(reference_count / self.yellow_count),
        )

    def _sample_nonoverlapping(self, diameters: np.ndarray) -> np.ndarray:
        positions: list[tuple[float, float]] = []
        radii: list[float] = []
        for diameter in diameters:
            radius = float(diameter) / 2.0
            for _ in range(5000):
                radial = (self.aperture_radius - radius) * math.sqrt(float(self.rng.random()))
                angle = float(self.rng.uniform(0.0, 2.0 * math.pi))
                candidate = (radial * math.cos(angle), radial * math.sin(angle))
                if all(
                    math.dist(candidate, existing) >= radius + existing_radius + self.min_gap
                    for existing, existing_radius in zip(positions, radii)
                ):
                    positions.append(candidate)
                    radii.append(radius)
                    break
            else:
                raise RuntimeError("Unable to place a non-overlapping ANS dot array")
        return np.asarray(positions, dtype=float)

    def draw(self) -> None:
        self.blue.draw()
        self.yellow.draw()


def register_dot_array_stimulus(stim_bank, settings) -> None:
    @stim_bank.define("intermixed_dot_array")
    def _factory(
        win,
        blue_count=8,
        yellow_count=6,
        visual_control="equal_average_size",
        seed=0,
        **overrides,
    ):
        params = {
            "aperture_radius_deg": float(settings.aperture_radius_deg),
            "dot_diameter_deg": float(settings.dot_diameter_deg),
            "min_gap_deg": float(settings.min_gap_deg),
            "blue_color": str(settings.blue_color),
            "yellow_color": str(settings.yellow_color),
        }
        params.update(overrides)
        return IntermixedDotArrayStim(
            win,
            blue_count=int(blue_count),
            yellow_count=int(yellow_count),
            visual_control=str(visual_control),
            seed=int(seed),
            **params,
        )
