from agentkit import tool
from core.preprocessing import Lap


def create_lap_tools(laps: list[Lap]):

    @tool
    def list_laps() -> str:
        """
        Lista as voltas da telemetria disponíveis, com seus status e performance.
        """

        if not laps:
            return "Nenhuma volta foi encontrada."

        lines = []

        for lap in laps:
            lines.append(
                f"Lap {lap.number}: "
                f"status={lap.status.value}, "
                f"time={lap.duration:.3f}s, "
                f"distance={lap.distance_covered:.1f}m, "
                f"average_speed={lap.average_speed:.2f}, "
                f"stopped_ratio={lap.stopped_ratio:.2f}"
            )

        valid_laps = [lap.number for lap in laps if lap.status.value == "valid"]

        lines.append(f"Valid laps: {valid_laps}")

        return "\n".join(lines)

    return [list_laps]
