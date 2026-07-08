from app.scan_engine.handlers import (
    BuildTechnicalManifestHandler,
    NotImplementedHandler,
    ValidateScopeHandler,
)
from app.scan_engine.manifest import TechnicalManifestBuilder
from app.scan_engine.registry import StepDefinition, StepRegistry


PIPELINE_VERSION = "scan-manifest-v1"


def build_default_registry() -> StepRegistry:
    registry = StepRegistry()
    not_implemented = NotImplementedHandler()

    definitions = (
        StepDefinition(
            key="validate_scope",
            position=10,
            weight=10,
            handler=ValidateScopeHandler(),
        ),
        StepDefinition(
            key="collect_channel",
            position=20,
            weight=10,
            handler=not_implemented,
        ),
        StepDefinition(
            key="collect_content",
            position=30,
            weight=20,
            handler=not_implemented,
        ),
        StepDefinition(
            key="collect_audience",
            position=40,
            weight=20,
            handler=not_implemented,
        ),
        StepDefinition(
            key="normalize_data",
            position=50,
            weight=15,
            handler=not_implemented,
        ),
        StepDefinition(
            key="analyze",
            position=60,
            weight=15,
            handler=not_implemented,
        ),
        StepDefinition(
            key="build_report",
            position=70,
            weight=10,
            handler=BuildTechnicalManifestHandler(
                TechnicalManifestBuilder()
            ),
        ),
    )
    for definition in definitions:
        registry.register(definition)
    return registry
