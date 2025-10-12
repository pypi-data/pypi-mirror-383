import os
from typing import Any

from langfuse import Langfuse

from ..config import config


class PlaybooksLangfuseSpan:
    def update(self, **kwargs: Any) -> None:
        pass

    def generation(self, **kwargs: Any) -> None:
        pass

    def span(self, **kwargs: Any) -> None:
        return PlaybooksLangfuseSpan()


class PlaybooksLangfuseInstance:
    def trace(self, **kwargs: Any) -> None:
        return PlaybooksLangfuseSpan()

    def flush(self) -> None:
        pass


class LangfuseHelper:
    """A singleton helper class for Langfuse telemetry and tracing.

    This class provides centralized access to Langfuse for observability and
    tracing of LLM operations throughout the application.
    """

    langfuse: Langfuse | None = None

    @classmethod
    def instance(cls) -> Langfuse | None:
        """Get or initialize the Langfuse singleton instance.

        Creates the Langfuse client on first call using environment variables.
        Returns None if environment variables are not set.

        Returns:
            Langfuse: The initialized Langfuse client instance, or None
        """
        if cls.langfuse is None:
            # Check if Langfuse is enabled via config system first, then env fallback
            langfuse_enabled = False
            try:
                langfuse_enabled = config.langfuse.enabled
            except Exception:
                # Fallback to environment variable if config loading fails
                langfuse_enabled = (
                    os.getenv("LANGFUSE_ENABLED", "false").lower() == "true"
                )

            if not langfuse_enabled:
                cls.langfuse = PlaybooksLangfuseInstance()
            else:
                cls.langfuse = Langfuse(
                    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
                    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
                    host=os.getenv("LANGFUSE_HOST"),
                )
        return cls.langfuse

    @classmethod
    def flush(cls) -> None:
        """Flush any buffered Langfuse telemetry data to the server.

        This method should be called when immediate data transmission is needed,
        such as before application shutdown or after important operations.
        """
        if cls.langfuse:
            cls.langfuse.flush()
