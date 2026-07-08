from dataclasses import dataclass

from app.scan_engine.types import ScanStepHandler


@dataclass(frozen=True)
class StepDefinition:
    key: str
    position: int
    weight: int
    handler: ScanStepHandler


class StepRegistry:
    def __init__(self) -> None:
        self._definitions: dict[str, StepDefinition] = {}

    def register(self, definition: StepDefinition) -> None:
        if definition.key in self._definitions:
            raise ValueError(
                f"Step '{definition.key}' is already registered"
            )
        if definition.weight <= 0:
            raise ValueError("Step weight must be positive")
        if any(
            existing.position == definition.position
            for existing in self._definitions.values()
        ):
            raise ValueError(
                f"Step position {definition.position} is already registered"
            )
        self._definitions[definition.key] = definition

    def get(self, key: str) -> StepDefinition:
        try:
            return self._definitions[key]
        except KeyError as error:
            raise KeyError(f"No handler registered for step '{key}'") from error

    @property
    def definitions(self) -> tuple[StepDefinition, ...]:
        return tuple(
            sorted(
                self._definitions.values(),
                key=lambda definition: definition.position,
            )
        )

    def validate(self) -> None:
        definitions = self.definitions
        if not definitions:
            raise ValueError("A scan pipeline requires at least one step")
        if definitions[-1].key != "build_report":
            raise ValueError(
                "The build_report step must be the final pipeline step"
            )
