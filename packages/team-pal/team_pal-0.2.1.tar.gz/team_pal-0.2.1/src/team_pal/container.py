"""Simple dependency injection container used across the codebase."""

from __future__ import annotations

from typing import Any, Callable, Literal

ProviderScope = Literal["singleton", "transient"]
Provider = Callable[["DependencyContainer"], Any]


class ProviderNotFoundError(KeyError):
    """Raised when a provider cannot be found in the container."""


class DependencyContainer:
    """Minimalistic registry supporting singleton and transient providers."""

    def __init__(self) -> None:
        self._providers: dict[str, Provider] = {}
        self._scopes: dict[str, ProviderScope] = {}
        self._instances: dict[str, Any] = {}

    def register_instance(self, key: str, instance: Any) -> None:
        """Register a concrete instance under ``key``."""

        self._instances[key] = instance
        # Ensure factories do not override explicit instance registrations.
        self._providers.pop(key, None)
        self._scopes[key] = "singleton"

    def register_factory(self, key: str, factory: Provider, *, scope: ProviderScope = "transient") -> None:
        """Register a factory that creates objects on demand."""

        if scope not in ("singleton", "transient"):
            raise ValueError(f"Unsupported provider scope: {scope}")

        self._providers[key] = factory
        self._scopes[key] = scope
        if scope == "transient" and key in self._instances:
            self._instances.pop(key, None)

    def resolve(self, key: str) -> Any:
        """Resolve an instance registered under ``key``."""

        if key in self._instances:
            return self._instances[key]

        if key not in self._providers:
            raise ProviderNotFoundError(key)

        provider = self._providers[key]
        scope = self._scopes.get(key, "transient")
        instance = provider(self)
        if scope == "singleton":
            self._instances[key] = instance
        return instance

    def clear(self) -> None:
        """Remove all registered providers and instances."""

        self._providers.clear()
        self._instances.clear()
        self._scopes.clear()


__all__ = ["DependencyContainer", "Provider", "ProviderScope", "ProviderNotFoundError"]
