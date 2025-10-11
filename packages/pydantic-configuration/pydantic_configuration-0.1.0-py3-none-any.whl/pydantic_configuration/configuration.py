from abc import ABC, abstractmethod
from pathlib import Path

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    YamlConfigSettingsSource,
)


class AbstractConfig(BaseSettings, ABC):
    @abstractmethod
    def _env_file(self) -> Path:
        """Path to the .env file."""
        pass

    @abstractmethod
    def _yaml_file(self) -> Path:
        """Path to the .yaml file."""
        pass

    # model_config = SettingsConfigDict(
    #     env_file=str(_env_file),
    #     yaml_file=str(_yaml_file),
    # )

    def __init__(self, **data):
        self.model_config["env_file"] = str(self._env_file())
        self.model_config["yaml_file"] = str(self._yaml_file())
        super().__init__(**data)

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customise settings sources."""
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )
