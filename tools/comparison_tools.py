import pandas as pd

from agentkit import tool
from core.preprocessing import Lap


def _section_time(
    data: pd.DataFrame,
    start_distance: float,
    end_distance: float,
) -> float:
    section = data[
        (data["LAP_DISTANCE"] >= start_distance) & (data["LAP_DISTANCE"] < end_distance)
    ]

    if section.empty:
        return 0.0

    return float(section["time"].iloc[-1] - section["time"].iloc[0])


def create_comparison_tools(laps: list[Lap]):

    @tool
    def compare_laps(
        target_lap: int,
        reference_lap: int,
    ) -> str:
        """
        Compara duas voltas validas e identifica onde a volta alvo perde ou ganha tempo em relação a volta de referência.
        """

        target = next(
            (lap for lap in laps if lap.number == target_lap),
            None,
        )

        reference = next(
            (lap for lap in laps if lap.number == reference_lap),
            None,
        )

        if target is None:
            return f"Volta alvo não encontrada: {target_lap}"

        if reference is None:
            return f"Volta de referência não encontrada: {reference_lap}"

        if target.status.value != "valid":
            return (
                f"A volta alvo {target_lap} não é valida. Status: {target.status.value}"
            )

        if reference.status.value != "valid":
            return f"A volta de referência {reference_lap} não é valida. Status: {reference.status.value}"

        target_time = target.duration
        reference_time = reference.duration

        time_difference = target_time - reference_time

        track_length = min(
            target.end_distance,
            reference.end_distance,
        )

        section_count = 5
        section_length = track_length / section_count

        sections = []

        for i in range(section_count):
            start_distance = i * section_length
            end_distance = (i + 1) * section_length

            target_section_time = _section_time(
                target.data,
                start_distance,
                end_distance,
            )

            reference_section_time = _section_time(
                reference.data,
                start_distance,
                end_distance,
            )

            difference = target_section_time - reference_section_time

            sections.append(
                {
                    "number": i + 1,
                    "start": start_distance,
                    "end": end_distance,
                    "target_time": target_section_time,
                    "reference_time": reference_section_time,
                    "difference": difference,
                }
            )

        lines = [
            f"Target lap: {target_lap}",
            f"Reference lap: {reference_lap}",
            f"Target time: {target_time:.3f}s",
            f"Reference time: {reference_time:.3f}s",
            f"Total time difference: {time_difference:+.3f}s",
            "",
            "Time difference by section:",
        ]

        for section in sections:
            lines.append(
                f"Section {section['number']}: "
                f"{section['start']:.0f}m - "
                f"{section['end']:.0f}m | "
                f"target={section['target_time']:.3f}s | "
                f"reference={section['reference_time']:.3f}s | "
                f"difference={section['difference']:+.3f}s"
            )

        return "\n".join(lines)

    return [compare_laps]
