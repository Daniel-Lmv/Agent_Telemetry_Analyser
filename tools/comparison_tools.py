import json

from agent.state import AnalysisState
from agentkit import tool


def create_comparison_tools(
    laps,
    state: AnalysisState,
):
    @tool
    def compare_laps(
        target_lap: int,
        reference_lap: int,
    ):
        """
        Compara uma volta analisada com uma volta de referência.

        Calcula a diferença total de tempo e divide a pista em cinco
        setores para identificar onde ocorreu a maior perda de tempo.

        O resultado da comparação também é armazenado no estado compartilhado
        da análise.
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
            return f"Target lap {target_lap} not found."

        if reference is None:
            return f"Reference lap {reference_lap} not found."

        if target.status.value != "valid":
            return (
                f"Target lap {target_lap} is not valid. Status: {target.status.value}"
            )

        if reference.status.value != "valid":
            return (
                f"Reference lap {reference_lap} is not valid. "
                f"Status: {reference.status.value}"
            )

        if target_lap == reference_lap:
            return "Target lap and reference lap must be different."

        # ---------------------------------------------------------
        # Tempo total das voltas
        # ---------------------------------------------------------

        target_time = target.duration
        reference_time = reference.duration

        total_time_difference = target_time - reference_time

        # ---------------------------------------------------------
        # Comprimento utilizado para comparação
        # ---------------------------------------------------------

        track_length = min(
            target.end_distance,
            reference.end_distance,
        )

        if track_length <= 0:
            return "Unable to determine a valid track length."

        # ---------------------------------------------------------
        # Divisão da pista em 5 setores
        # ---------------------------------------------------------

        number_of_sections = 5
        section_length = track_length / number_of_sections

        sections = []

        for section in range(1, number_of_sections + 1):
            start_distance = (section - 1) * section_length
            end_distance = section * section_length

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

            # -----------------------------------------------------
            # Tempo do setor
            # -----------------------------------------------------

            target_section_time = (
                target_section["time"].iloc[-1] - target_section["time"].iloc[0]
            )

            reference_section_time = (
                reference_section["time"].iloc[-1] - reference_section["time"].iloc[0]
            )

            difference = target_section_time - reference_section_time

            sections.append(
                {
                    "section": section,
                    "start_distance": round(start_distance, 3),
                    "end_distance": round(end_distance, 3),
                    "target_time": round(
                        float(target_section_time),
                        4,
                    ),
                    "reference_time": round(
                        float(reference_section_time),
                        4,
                    ),
                    "difference": round(
                        float(difference),
                        4,
                    ),
                }
            )

        if not sections:
            return "Unable to calculate sector comparison."

        # ---------------------------------------------------------
        # Identifica o setor com maior perda
        #
        # Quanto maior o valor, maior o tempo perdido.
        # ---------------------------------------------------------

        main_loss = max(
            sections,
            key=lambda section: section["difference"],
        )

        # ---------------------------------------------------------
        # Atualiza o estado compartilhado
        # ---------------------------------------------------------

        state.set_laps(
            target_lap=target_lap,
            reference_lap=reference_lap,
        )

        state.set_comparison(
            total_time_difference=float(total_time_difference),
            main_loss_section=main_loss["section"],
            main_loss=float(main_loss["difference"]),
        )

        state.add_observation(
            f"Comparison completed between lap {target_lap} "
            f"and lap {reference_lap}. "
            f"Main loss was identified in section "
            f"{main_loss['section']}."
        )

        # ---------------------------------------------------------
        # Resultado retornado para o agente
        # ---------------------------------------------------------

        result = {
            "target_lap": target_lap,
            "reference_lap": reference_lap,
            "target_time": round(float(target_time), 4),
            "reference_time": round(float(reference_time), 4),
            "total_time_difference": round(
                float(total_time_difference),
                4,
            ),
            "main_loss_section": main_loss["section"],
            "main_loss": main_loss["difference"],
            "main_loss_start_distance": main_loss["start_distance"],
            "main_loss_end_distance": main_loss["end_distance"],
            "sections": sections,
        }

        return json.dumps(
            result,
            ensure_ascii=False,
        )

    return [compare_laps]
