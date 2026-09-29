import pandas as pd

from agentkit import tool
from core.preprocessing import Lap


def _analyze_signal(
    data: pd.DataFrame,
    column: str,
) -> dict:
    if column not in data.columns:
        return {
            "available": False,
        }

    values = data[column].dropna()

    if values.empty:
        return {
            "available": False,
        }

    return {
        "available": True,
        "mean": float(values.mean()),
        "minimum": float(values.min()),
        "maximum": float(values.max()),
    }


def create_section_tools(laps: list[Lap]):

    @tool
    def analyze_section(
        target_lap: int,
        reference_lap: int,
        start_distance: float,
        end_distance: float,
    ) -> str:
        """
        Analisa um sinal de telemetria dentro de um setor específico, comparando a volta alvo com a volta de referência.
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

        if start_distance >= end_distance:
            return "O início da seção deve ser menor que o final da seção"

        def select_section(lap: Lap) -> pd.DataFrame:
            return lap.data[
                (lap.data["LAP_DISTANCE"] >= start_distance)
                & (lap.data["LAP_DISTANCE"] < end_distance)
            ]

        target_data = select_section(target)
        reference_data = select_section(reference)

        if target_data.empty:
            return f"Não existem dados da volta {target_lap} nessa seção"

        if reference_data.empty:
            return f"Não existem dados da volta {reference_lap} nessa seção"

        signals = [
            "SPEED",
            "BRAKE",
            "THROTTLE",
            "RPM",
            "STEERING",
        ]

        lines = [
            f"Section: {start_distance:.1f}m - {end_distance:.1f}m",
            f"Target lap: {target_lap}",
            f"Rerefence lap: {reference_lap}",
            "",
        ]

        for signal in signals:
            target_stats = _analyze_signal(
                target_data,
                signal,
            )

            reference_stats = _analyze_signal(
                reference_data,
                signal,
            )

            if not target_stats["available"]:
                continue

            if not reference_stats["available"]:
                continue

            mean_difference = target_stats["mean"] - reference_stats["mean"]

            min_difference = target_stats["minimum"] - reference_stats["minimum"]

            max_difference = target_stats["maximum"] - reference_stats["maximum"]

            lines.append(f"{signal}")

            lines.append(
                f" target mean={target_stats['mean']:.3f}"
                f", reference mean={reference_stats['mean']:.3f}"
                f", difference={mean_difference:+.3f}"
            )

            lines.append(
                f" target min={target_stats['minimum']:.3f}"
                f", reference min={reference_stats['minimum']:.3f}"
                f", difference={min_difference:+.3f}"
            )

            lines.append(
                f" target max={target_stats['maximum']:.3f}"
                f", reference max={reference_stats['maximum']:.3f}"
                f", difference={max_difference:+.3f}"
            )

            lines.append("")

        return "\n".join(lines)

    return [analyze_section]
