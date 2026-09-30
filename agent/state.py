from dataclasses import dataclass, field


@dataclass
class AnalysisState:
    """
    Estado compartilhado durante uma análise de telemetria.

    O estado é atualizado pelas ferramentas conforme o agente
    executa as etapas da análise.
    """

    # Voltas envolvidas na análise
    target_lap: int | None = None
    reference_lap: int | None = None

    # Resultado da comparação geral
    compared: bool = False
    total_time_difference: float | None = None
    main_loss_section: int | None = None
    main_loss: float | None = None

    # Setores que já foram analisados
    analyzed_sections: list[int] = field(default_factory=list)

    # Evidências encontradas durante as análises
    evidence: list[dict] = field(default_factory=list)

    # Mensagens/observações produzidas pelas ferramentas
    observations: list[str] = field(default_factory=list)

    def set_laps(self, target_lap: int, reference_lap: int) -> None:
        """Define as voltas utilizadas na análise."""
        self.target_lap = target_lap
        self.reference_lap = reference_lap

    def set_comparison(
        self,
        total_time_difference: float,
        main_loss_section: int,
        main_loss: float,
    ) -> None:
        """Registra o resultado da comparação entre as voltas."""
        self.compared = True
        self.total_time_difference = total_time_difference
        self.main_loss_section = main_loss_section
        self.main_loss = main_loss

    def add_section(self, section: int) -> None:
        """Registra um setor que já foi analisado."""
        if section not in self.analyzed_sections:
            self.analyzed_sections.append(section)

    def add_evidence(
        self,
        metric: str,
        target_value: float,
        reference_value: float,
        difference: float,
        interpretation: str,
        section: int | None = None,
    ) -> None:
        """Adiciona uma evidência quantitativa encontrada."""
        self.evidence.append(
            {
                "section": section,
                "metric": metric,
                "target_value": target_value,
                "reference_value": reference_value,
                "difference": difference,
                "interpretation": interpretation,
            }
        )

    def add_observation(self, observation: str) -> None:
        """Adiciona uma observação ao estado."""
        self.observations.append(observation)

    def has_analyzed_section(self, section: int) -> bool:
        """Verifica se determinado setor já foi analisado."""
        return section in self.analyzed_sections

    def reset(self) -> None:
        """Limpa o estado para iniciar uma nova análise."""
        self.target_lap = None
        self.reference_lap = None

        self.compared = False
        self.total_time_difference = None
        self.main_loss_section = None
        self.main_loss = None

        self.analyzed_sections.clear()
        self.evidence.clear()
        self.observations.clear()

    def summary(self) -> dict:
        """Retorna um resumo estruturado do estado atual."""
        return {
            "target_lap": self.target_lap,
            "reference_lap": self.reference_lap,
            "compared": self.compared,
            "total_time_difference": self.total_time_difference,
            "main_loss_section": self.main_loss_section,
            "main_loss": self.main_loss,
            "analyzed_sections": self.analyzed_sections.copy(),
            "evidence_count": len(self.evidence),
            "observation_count": len(self.observations),
        }
