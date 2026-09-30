import json

import pandas as pd

from agentkit import tool


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


def create_comparison_tools(laps):

    @tool
    def compare_laps(target_lap: int, reference_lap: int):
        """
        Compara duas voltas válidas e identifica onde houve perda ou ganho
        de tempo. Retorna a diferença total e a diferença por setor.
        """

        target = next((lap for lap in laps if lap.number == target_lap), None)
        reference = next((lap for lap in laps if lap.number == reference_lap), None)

        if target is None:
            return f"Target lap {target_lap} not found."

        if reference is None:
            return f"Reference lap {reference_lap} not found."

        if target.status.value != "valid":
            return f"Target lap {target_lap} is not valid."

        if reference.status.value != "valid":
            return f"Reference lap {reference_lap} is not valid."

        total_difference = target.duration - reference.duration

        track_length = min(target.end_distance, reference.end_distance)

        section_length = track_length / 5

        sections = []

        for i in range(5):
            start_distance = i * section_length
            end_distance = (i + 1) * section_length

            target_section = target.data[
                (target.data["LAP_DISTANCE"] >= start_distance)
                & (target.data["LAP_DISTANCE"] < end_distance)
            ]

            reference_section = reference.data[
                (reference.data["LAP_DISTANCE"] >= start_distance)
                & (reference.data["LAP_DISTANCE"] < end_distance)
            ]

            if target_section.empty or reference_section.empty:
                continue

            target_time = (
                target_section["time"].iloc[-1] - target_section["time"].iloc[0]
            )

            reference_time = (
                reference_section["time"].iloc[-1] - reference_section["time"].iloc[0]
            )

            difference = target_time - reference_time

            sections.append(
                {
                    "section": i + 1,
                    "start_distance": round(float(start_distance), 3),
                    "end_distance": round(float(end_distance), 3),
                    "target_time": round(float(target_time), 3),
                    "reference_time": round(float(reference_time), 3),
                    "difference": round(float(difference), 3),
                }
            )

        if not sections:
            return "No comparable sections found."

        # Maior valor positivo = maior perda de tempo.
        main_loss = max(sections, key=lambda section: section["difference"])

        result = {
            "target_lap": target_lap,
            "reference_lap": reference_lap,
            "target_time": round(float(target.duration), 3),
            "reference_time": round(float(reference.duration), 3),
            "total_time_difference": round(float(total_difference), 3),
            "main_loss_section": main_loss["section"],
            "main_loss": main_loss["difference"],
            "main_loss_start_distance": main_loss["start_distance"],
            "main_loss_end_distance": main_loss["end_distance"],
            "sections": sections,
        }

        return json.dumps(result, ensure_ascii=False)

    return [compare_laps]
