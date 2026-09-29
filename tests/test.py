from core.preprocessing import detect_lap_boundaries, split_laps
from core.telemetry import Telemetry

telemetry = Telemetry.from_file("data/sessao.csv")

boundaries = detect_lap_boundaries(telemetry.data)

print("Limites encontrados:")
print(boundaries)

laps = split_laps(telemetry.data)

for lap in laps:
    speed = lap.data["SPEED"]

    stopped_ratio = (speed <= 1.0).mean()

    print(
        f"Lap {lap.number}: "
        f"amostras={len(lap.data)}, "
        f"velocidade média={speed.mean():.2f}, "
        f"parado={stopped_ratio * 100:.2f}%"
    )
