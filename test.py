from core.preprocessing import (
    get_valid_laps,
    preprocess_telemetry,
)
from core.telemetry import Telemetry

telemetry = Telemetry.from_file("data/sessao.csv")

laps, track_length = preprocess_telemetry(telemetry.data)

print(f"Comprimento estimado do circuito: {track_length:.2f} m")

for lap in laps:
    print(
        f"Lap {lap.number}: "
        f"{lap.status.value} | "
        f"{lap.duration:.2f}s | "
        f"{lap.end_distance:.2f}m"
    )

valid_laps = get_valid_laps(laps)

print("\nVoltas válidas:")

for lap in valid_laps:
    print(f"Lap {lap.number}: {lap.duration:.2f}s")
