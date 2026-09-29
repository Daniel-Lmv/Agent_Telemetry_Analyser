from core.preprocessing import preprocess_telemetry
from core.telemetry import Telemetry
from tools.comparison_tools import create_comparison_tools
from tools.lap_tools import create_lap_tools
from tools.section_tools import create_section_tools

telemetry = Telemetry.from_file("data/sessao.csv")

laps, track_length = preprocess_telemetry(telemetry.data)

lap_tools = create_lap_tools(laps)
comparison_tools = create_comparison_tools(laps)
section_tools = create_section_tools(laps)

list_laps = lap_tools[0]
compare_laps = comparison_tools[0]
analyze_section = section_tools[0]

print(list_laps())

print("\n" + "=" * 60 + "\n")

print(
    compare_laps(
        target_lap=7,
        reference_lap=9,
    )
)

print("\n" + "=" * 60 + "\n")

print(
    analyze_section(
        target_lap=7,
        reference_lap=9,
        start_distance=3000,
        end_distance=4000,
    )
)
