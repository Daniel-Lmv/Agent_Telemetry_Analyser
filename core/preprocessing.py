from dataclasses import dataclass
from enum import Enum

import pandas as pd


class LapStatus(Enum):
    VALID = "valid"
    INCOMPLETE = "incomplete"
    PIT = "pit"
    PARTIAL_START = "partial_start"


@dataclass
class Lap:
    """
    Representa uma volta individual da sessão.
    """

    number: int
    data: pd.DataFrame
    status: LapStatus = LapStatus.VALID

    @property
    def start_index(self) -> int:
        return self.data.index[0]

    @property
    def end_index(self) -> int:
        return self.data.index[-1]

    @property
    def start_distance(self) -> float:
        return float(self.data["LAP_DISTANCE"].iloc[0])

    @property
    def end_distance(self) -> float:
        return float(self.data["LAP_DISTANCE"].iloc[-1])

    @property
    def duration(self) -> float:
        return float(self.data["time"].iloc[-1] - self.data["time"].iloc[0])

    @property
    def sample_count(self) -> int:
        return len(self.data)

    @property
    def average_speed(self) -> float:
        return float(self.data["SPEED"].mean())

    @property
    def stopped_ratio(self) -> float:
        """
        Proporção das amostras em que o carro estava praticamente parado.
        """
        return float((self.data["SPEED"] <= 1.0).mean())

    @property
    def distance_covered(self) -> float:
        return self.end_distance - self.start_distance


def detect_lap_boundaries(
    data: pd.DataFrame,
    distance_column: str = "LAP_DISTANCE",
    reset_threshold: float = 1000.0,
) -> list[int]:
    """
    Detecta os pontos onde uma volta termina e outra começa.

    A mudança de volta é identificada por uma mudança grande no valor de LAP_DISTANCE.

    O reset_threshold não representa o tamanho do circuito. Ele apenas é um valor suficientemente
    grande para diferenciar um reset de volta de pequenas oscilações existentes na telemetria.
    """

    if distance_column not in data.columns:
        raise ValueError(f"Coluna obrigatória não encontrada: {distance_column}")

    distance = data[distance_column]

    changes = distance.diff()

    boundaries = changes[changes < -reset_threshold].index.tolist()

    return boundaries


def split_laps(
    data: pd.DataFrame,
    reset_threshold: float = 1000.0,
) -> list[Lap]:
    """
    Divide a telemetria em segmentos correspondentes às voltas

    Apenas identifica os segmentos de voltas, não classifica as voltas.
    """

    boundaries = detect_lap_boundaries(
        data,
        reset_threshold=reset_threshold,
    )

    laps: list[Lap] = []

    start = 0

    for end in boundaries:
        lap_data = data.iloc[start:end].copy()

        if not lap_data.empty:
            laps.append(
                Lap(
                    number=len(laps) + 1,
                    data=lap_data,
                )
            )

        start = end

    # Último segmento da sessão.
    if start < len(data):
        lap_data = data.iloc[start:].copy()

        if not lap_data.empty:
            laps.append(
                Lap(
                    number=len(laps) + 1,
                    data=lap_data,
                )
            )

    return laps


def estimate_track_length(
    laps: list[Lap],
    minimum_laps: int = 2,
) -> float:
    """
    Estima o comprimento do circuito a partir das voltas.

    A estimativa utiliza a mediana das maiores distâncias percorridas pelos segmentos da sessão.

    O valor retornado representa uma estimativa da distância da uma volta completa, e não uma medição oficial da pista.
    """

    if len(laps) < minimum_laps:
        raise ValueError(
            "Não há voltas suficientes para estimar o comprimento do circuito."
        )

    distances = sorted(lap.end_distance for lap in laps)

    # Utiliza a metade superior das distâncias, voltas incompletas tendem a possuir uma distância menor.
    upper_half = distances[len(distances) // 2 :]

    if not upper_half:
        raise ValueError(
            "Não foi possível encontrar distâncias suficientes para estimar o circuito."
        )

    return float(pd.Series(upper_half).median())


def classify_lap(
    lap: Lap,
    track_length: float,
    *,
    completion_ratio: float = 0.95,
    partial_start_ratio: float = 0.01,
    pit_stop_ratio: float = 0.20,
) -> LapStatus:
    """
    Classifica uma volta utilizando proporções relativas ao comprimento estimado do circuito.

    Parametros:

    completion_ratio:
        percentual mínimo do circuito que deve ser percorrido para considerar que uma volta chegou ao fim.

    partial_start_ratio:
        percentual do circuito a partir do qual o início da volta é considerado distante demais da linha de início.

    pit_stop_ratio:
        percentual de amostras com velocidade praticamente zero, usado para identificar uma parada significativa.
    """

    if track_length <= 0:
        raise ValueError("O comprimento do circuito deve ser maior que zero.")

    start_ratio = lap.start_distance / track_length
    end_ratio = lap.end_distance / track_length

    # Verificar se a volta percorreu o minimo para ser considerada completa
    if end_ratio < completion_ratio:
        return LapStatus.INCOMPLETE

    # Verificar se a volta começou depois de uma parte significativa do circuito.
    if start_ratio >= partial_start_ratio:
        return LapStatus.PARTIAL_START

    # Uma volta completa que passou uma quantidade significativa de tempo parada é considerada uma volta de Pits
    if lap.stopped_ratio >= pit_stop_ratio:
        return LapStatus.PIT

    return LapStatus.VALID


def classify_all_laps(
    laps: list[Lap],
    track_length: float,
    *,
    completion_ratio: float = 0.95,
    partial_start_ratio: float = 0.01,
    pit_stop_ratio: float = 0.20,
) -> list[Lap]:
    """
    Classifica todas as voltas de uma sessão
    """

    for lap in laps:
        lap.status = classify_lap(
            lap,
            track_length,
            completion_ratio=completion_ratio,
            partial_start_ratio=partial_start_ratio,
            pit_stop_ratio=pit_stop_ratio,
        )

    return laps


def get_valid_laps(
    laps: list[Lap],
) -> list[Lap]:
    """
    Retorna somente as voltas consideradas válidas para comparação de desempenho.
    """

    return [lap for lap in laps if lap.status == LapStatus.VALID]


def preprocess_telemetry(
    data: pd.DataFrame,
    *,
    reset_threshold: float = 1000.0,
    completion_ratio: float = 0.95,
    partial_start_ratio: float = 0.01,
    pit_stop_ratio: float = 0.20,
) -> tuple[list[Lap], float]:
    """
    Executa todo o pipeline de preprocessing da sessão.

    Retorna:

    laps:
        todas as voltas identificadas e classificadas.

    track_length:
        estimativa do comprimento do circuito.
    """

    laps = split_laps(
        data,
        reset_threshold=reset_threshold,
    )

    track_length = estimate_track_length(laps)

    classify_all_laps(
        laps,
        track_length,
        completion_ratio=completion_ratio,
        partial_start_ratio=partial_start_ratio,
        pit_stop_ratio=pit_stop_ratio,
    )

    return laps, track_length
