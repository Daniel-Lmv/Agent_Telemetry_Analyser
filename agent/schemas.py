from pydantic import BaseModel, Field


class TelemetryEvidence(BaseModel):
    """Evidência quantitativa utilizada para justificar uma conclusão."""

    metric: str = Field(
        description="Nome da métrica analisada, por exemplo SPEED, BRAKE ou THROTTLE."
    )

    target_value: float = Field(description="Valor da métrica na volta analisada.")

    reference_value: float = Field(
        description="Valor da métrica na volta de referência."
    )

    difference: float = Field(
        description="Diferença entre o valor da volta analisada e da referência."
    )

    interpretation: str = Field(
        description="Descrição objetiva do que a diferença observada indica."
    )


class SectionAnalysis(BaseModel):
    """Análise quantitativa de um setor onde houve perda de tempo."""

    section: int = Field(description="Número do setor analisado.")

    start_distance: float = Field(description="Distância inicial do setor em metros.")

    end_distance: float = Field(description="Distância final do setor em metros.")

    time_difference: float = Field(
        description="Diferença de tempo do setor em segundos. Valor positivo significa perda de tempo da volta analisada."
    )

    evidence: list[TelemetryEvidence] = Field(
        description="Evidências quantitativas encontradas na telemetria do setor."
    )


class TelemetryAnalysis(BaseModel):
    """Resultado estruturado da análise de uma volta de telemetria."""

    target_lap: int = Field(description="Número da volta analisada.")

    reference_lap: int = Field(description="Número da volta utilizada como referência.")

    total_time_difference: float = Field(
        description="Diferença total de tempo entre a volta analisada e a referência, em segundos. Valor positivo significa que a volta analisada foi mais lenta."
    )

    main_loss_section: int = Field(
        description="Número do setor que apresentou a maior perda de tempo."
    )

    section_analysis: SectionAnalysis = Field(
        description="Análise detalhada do principal setor de perda."
    )

    explanation: str = Field(
        description="Explicação objetiva da perda de tempo baseada somente nas evidências disponíveis."
    )

    limitations: list[str] = Field(
        description="Limitações ou conclusões que não podem ser determinadas diretamente pela telemetria disponível."
    )
