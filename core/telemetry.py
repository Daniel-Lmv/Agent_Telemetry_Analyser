from pathlib import Path

import pandas as pd


class Telemetry:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    @classmethod
    def from_file(cls, path: str | Path) -> "Telemetry":
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Arquivo de telemetria não encontrado: {path}")

        # Lê um arquivo csv
        if path.suffix.lower() == ".csv":
            data = pd.read_csv(path)

        # Lê um arquivo json
        elif path.suffix.lower() == ".json":
            data = pd.read_json(path)

        # Erro para outros tipos de arquivos
        else:
            raise ValueError(f"Formato de arquivo não suportado: {path.suffix}")

        # Verifica se o arquivo não está vazio
        if data.empty:
            raise ValueError("O arquivo de telemetria está vazio.")

        return cls(data)

    @property
    def columns(self) -> list[str]:
        return self.data.columns.tolist()

    def __len__(self) -> int:
        return len(self.data)
