from agent.state import AnalysisState
from agentkit import tool


def create_section_tools(
    laps,
    state: AnalysisState,
):
    @tool
    def analyze_section(
        target_lap: int,
        reference_lap: int,
        section: int,
    ):
        """
        Analisa um setor específico comparando duas voltas.

        O setor deve ser informado como um número de 1 a 5.
        Os limites de distância são calculados automaticamente
        a partir do comprimento disponível da pista.

        A ferramenta calcula estatísticas de velocidade, freio,
        acelerador, RPM e direção, além de registrar as evidências
        encontradas no estado compartilhado da análise.
        """

        # ---------------------------------------------------------
        # Validação das voltas
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # Registra as voltas no estado
        # ---------------------------------------------------------

        state.set_laps(
            target_lap=target_lap,
            reference_lap=reference_lap,
        )

        # ---------------------------------------------------------
        # Validação do setor
        # ---------------------------------------------------------

        if section < 1 or section > 5:
            return "Section must be between 1 and 5."

        # ---------------------------------------------------------
        # Comprimento da pista
        # ---------------------------------------------------------

        track_length = min(
            target.end_distance,
            reference.end_distance,
        )

        if track_length <= 0:
            return "Unable to determine a valid track length."

        section_length = track_length / 5

        start_distance = (section - 1) * section_length

        end_distance = section * section_length

        # ---------------------------------------------------------
        # Seleção dos dados do setor
        # ---------------------------------------------------------

        target_section = target.data[
            (target.data["LAP_DISTANCE"] >= start_distance)
            & (target.data["LAP_DISTANCE"] < end_distance)
        ]

        reference_section = reference.data[
            (reference.data["LAP_DISTANCE"] >= start_distance)
            & (reference.data["LAP_DISTANCE"] < end_distance)
        ]

        if target_section.empty:
            return (
                f"No telemetry data found for target lap "
                f"{target_lap} in section {section}."
            )

        if reference_section.empty:
            return (
                f"No telemetry data found for reference lap "
                f"{reference_lap} in section {section}."
            )

        # ---------------------------------------------------------
        # Estatísticas
        # ---------------------------------------------------------

        def statistics(
            data,
            column: str,
        ) -> dict:

            values = data[column].dropna()

            if values.empty:
                return {
                    "mean": None,
                    "min": None,
                    "max": None,
                }

            return {
                "mean": float(values.mean()),
                "min": float(values.min()),
                "max": float(values.max()),
            }

        # ---------------------------------------------------------
        # Métricas utilizadas na análise
        # ---------------------------------------------------------

        metrics = [
            "SPEED",
            "BRAKE",
            "THROTTLE",
            "RPM",
            "STEERING",
        ]

        # ---------------------------------------------------------
        # Resultado
        # ---------------------------------------------------------

        result = [
            f"Section: {section}",
            (f"Distance: {start_distance:.3f}m - {end_distance:.3f}m"),
            f"Target lap: {target_lap}",
            f"Reference lap: {reference_lap}",
            "",
        ]

        # ---------------------------------------------------------
        # Análise das métricas
        # ---------------------------------------------------------

        for metric in metrics:
            if metric not in target_section.columns:
                continue

            if metric not in reference_section.columns:
                continue

            target_stats = statistics(
                target_section,
                metric,
            )

            reference_stats = statistics(
                reference_section,
                metric,
            )

            if target_stats["mean"] is None:
                continue

            if reference_stats["mean"] is None:
                continue

            mean_difference = target_stats["mean"] - reference_stats["mean"]

            min_difference = target_stats["min"] - reference_stats["min"]

            max_difference = target_stats["max"] - reference_stats["max"]

            result.append(f"{metric}:")

            result.append(f"  Target mean: {target_stats['mean']:.3f}")

            result.append(f"  Reference mean: {reference_stats['mean']:.3f}")

            result.append(f"  Mean difference: {mean_difference:+.3f}")

            result.append(f"  Target min: {target_stats['min']:.3f}")

            result.append(f"  Reference min: {reference_stats['min']:.3f}")

            result.append(f"  Min difference: {min_difference:+.3f}")

            result.append(f"  Target max: {target_stats['max']:.3f}")

            result.append(f"  Reference max: {reference_stats['max']:.3f}")

            result.append(f"  Max difference: {max_difference:+.3f}")

            result.append("")

            # -----------------------------------------------------
            # Registra evidência no estado
            # -----------------------------------------------------

            interpretation = f"{metric} mean difference: {mean_difference:+.3f}"

            state.add_evidence(
                metric=metric,
                target_value=target_stats["mean"],
                reference_value=reference_stats["mean"],
                difference=mean_difference,
                interpretation=interpretation,
                section=section,
            )

        # ---------------------------------------------------------
        # Registra setor analisado
        # ---------------------------------------------------------

        state.add_section(section)

        state.add_observation(
            f"Section {section} analyzed between "
            f"distance {start_distance:.3f}m and "
            f"{end_distance:.3f}m."
        )

        return "\n".join(result)

    return [analyze_section]
