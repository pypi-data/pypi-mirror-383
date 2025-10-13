"""Core data structures used to model glitchlings and their interactions."""

import inspect
import logging
import os
import random
from enum import IntEnum, auto
from hashlib import blake2s
from typing import TYPE_CHECKING, Any, Callable, Protocol

_datasets_error: ModuleNotFoundError | None = None
try:  # pragma: no cover - optional dependency
    from datasets import Dataset as _DatasetsDataset
except ModuleNotFoundError as error:  # pragma: no cover - optional dependency
    _DatasetsDataset = None  # type: ignore[assignment]
    _datasets_error = error
else:
    _datasets_error = None

try:  # pragma: no cover - optional dependency
    from glitchlings._zoo_rust import (
        compose_glitchlings as _compose_glitchlings_rust,
        plan_glitchlings as _plan_glitchlings_rust,
    )
except ImportError:  # pragma: no cover - compiled extension not present
    _compose_glitchlings_rust = None
    _plan_glitchlings_rust = None


log = logging.getLogger(__name__)


_PIPELINE_FEATURE_FLAG_ENV = "GLITCHLINGS_RUST_PIPELINE"
_PIPELINE_ENABLE_VALUES = {"1", "true", "yes", "on"}
_PIPELINE_DISABLE_VALUES = {"0", "false", "no", "off"}


def _pipeline_feature_flag_enabled() -> bool:
    """Return ``True`` when the environment does not explicitly disable the Rust pipeline."""

    value = os.environ.get(_PIPELINE_FEATURE_FLAG_ENV)
    if value is None:
        return True

    normalized = value.strip().lower()
    if normalized in _PIPELINE_DISABLE_VALUES:
        return False

    if normalized in _PIPELINE_ENABLE_VALUES:
        return True

    return True

def _plan_glitchlings_python(
    specs: list[dict[str, Any]],
    master_seed: int,
) -> list[tuple[int, int]]:
    """Pure-Python fallback for orchestrating glitchlings in deterministic order."""

    master_seed_int = int(master_seed)
    planned: list[tuple[int, int, int, int, str]] = []
    for index, spec in enumerate(specs):
        name = str(spec["name"])
        scope = int(spec["scope"])
        order = int(spec["order"])
        derived_seed = Gaggle.derive_seed(master_seed_int, name, index)
        planned.append((index, derived_seed, scope, order, name))

    planned.sort(key=lambda entry: (entry[2], entry[3], entry[4], entry[0]))
    return [(index, seed) for index, seed, *_ in planned]


def _plan_glitchlings_with_rust(
    specs: list[dict[str, Any]],
    master_seed: int,
) -> list[tuple[int, int]] | None:
    """Attempt to obtain the orchestration plan from the compiled Rust module."""

    if _plan_glitchlings_rust is None:
        return None

    try:
        plan = _plan_glitchlings_rust(specs, int(master_seed))
    except Exception:  # pragma: no cover - defer to Python fallback on failure
        log.debug("Rust orchestration planning failed; falling back to Python plan", exc_info=True)
        return None

    return [(int(index), int(seed)) for index, seed in plan]


def _plan_glitchling_specs(
    specs: list[dict[str, Any]],
    master_seed: int | None,
) -> list[tuple[int, int]]:
    """Resolve orchestration order and seeds from glitchling specifications."""

    if master_seed is None:
        message = "Gaggle orchestration requires a master seed"
        raise ValueError(message)

    master_seed_int = int(master_seed)
    plan = _plan_glitchlings_with_rust(specs, master_seed_int)
    if plan is not None:
        return plan

    return _plan_glitchlings_python(specs, master_seed_int)


def _plan_glitchling_sequence(
    glitchlings: list["Glitchling"], master_seed: int | None
) -> list[tuple[int, int]]:
    """Derive orchestration plan for concrete glitchling instances."""

    specs = [
        {
            "name": glitchling.name,
            "scope": int(glitchling.level),
            "order": int(glitchling.order),
        }
        for glitchling in glitchlings
    ]
    return _plan_glitchling_specs(specs, master_seed)

if TYPE_CHECKING:  # pragma: no cover - typing only
    from datasets import Dataset  # type: ignore
elif _DatasetsDataset is not None:
    Dataset = _DatasetsDataset
else:

    class Dataset(Protocol):  # type: ignore[no-redef]
        """Typed stub mirroring the Hugging Face dataset interface used here."""

        def with_transform(self, function: Any) -> "Dataset": ...


def _is_transcript(
    value: Any,
    *,
    allow_empty: bool = True,
    require_all_content: bool = False,
) -> bool:
    """Return `True` when `value` appears to be a chat transcript."""

    if not isinstance(value, list):
        return False

    if not value:
        return allow_empty

    if not all(isinstance(turn, dict) for turn in value):
        return False

    if require_all_content:
        return all("content" in turn for turn in value)

    return "content" in value[-1]


class CorruptionCallable(Protocol):
    """Protocol describing a callable capable of corrupting text."""

    def __call__(self, text: str, *args: Any, **kwargs: Any) -> str: ...


# Text levels for glitchlings, to enforce a sort order
# Work from highest level down, because e.g.
# duplicating a word then adding a typo is potentially different than
# adding a typo then duplicating a word
class AttackWave(IntEnum):
    """Granularity of text that a glitchling corrupts."""

    DOCUMENT = auto()
    PARAGRAPH = auto()
    SENTENCE = auto()
    WORD = auto()
    CHARACTER = auto()


# Modifier for within the same attack wave
class AttackOrder(IntEnum):
    """Relative execution order for glitchlings within the same wave."""

    FIRST = auto()
    EARLY = auto()
    NORMAL = auto()
    LATE = auto()
    LAST = auto()


class Glitchling:
    """A single text corruption agent with deterministic behaviour."""

    def __init__(
        self,
        name: str,
        corruption_function: CorruptionCallable,
        scope: AttackWave,
        order: AttackOrder = AttackOrder.NORMAL,
        seed: int | None = None,
        pipeline_operation: Callable[["Glitchling"], dict[str, Any] | None] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a glitchling.

        Args:
            name: Human readable glitchling name.
            corruption_function: Callable used to transform text.
            scope: Text granularity on which the glitchling operates.
            order: Relative ordering within the same scope.
            seed: Optional seed for deterministic random behaviour.
            **kwargs: Additional parameters forwarded to the corruption callable.
        """

        # Each Glitchling maintains its own RNG for deterministic yet isolated behavior.
        # If no seed is supplied, we fall back to Python's default entropy.
        self.seed = seed
        self.rng: random.Random = random.Random(seed)
        self.name: str = name
        self.corruption_function: CorruptionCallable = corruption_function
        self.level: AttackWave = scope
        self.order: AttackOrder = order
        self._pipeline_descriptor_factory = pipeline_operation
        self.kwargs: dict[str, Any] = {}
        self._cached_rng_callable: CorruptionCallable | None = None
        self._cached_rng_expectation: bool | None = None
        for kw, val in kwargs.items():
            self.set_param(kw, val)

    def set_param(self, key: str, value: Any) -> None:
        """Persist a parameter for use by the corruption callable."""

        aliases = getattr(self, "_param_aliases", {})
        canonical = aliases.get(key, key)

        # Drop stale alias keys so we only forward canonical kwargs.
        self.kwargs.pop(key, None)
        for alias, target in aliases.items():
            if target == canonical:
                self.kwargs.pop(alias, None)

        self.kwargs[canonical] = value
        setattr(self, canonical, value)

        if canonical == "seed":
            self.reset_rng(value)

        for alias, target in aliases.items():
            if target == canonical:
                setattr(self, alias, value)

    def pipeline_operation(self) -> dict[str, Any] | None:
        """Return the Rust pipeline operation descriptor for this glitchling."""

        factory = self._pipeline_descriptor_factory
        if factory is None:
            return None

        return factory(self)

    def _corruption_expects_rng(self) -> bool:
        """Return `True` when the corruption function accepts an rng keyword."""

        cached_callable = self._cached_rng_callable
        cached_expectation = self._cached_rng_expectation
        corruption_function = self.corruption_function

        if (
            cached_callable is corruption_function
            and cached_expectation is not None
        ):
            return cached_expectation

        expects_rng = False
        try:
            signature = inspect.signature(corruption_function)
        except (TypeError, ValueError):
            signature = None

        if signature is not None:
            expects_rng = "rng" in signature.parameters

        self._cached_rng_callable = corruption_function
        self._cached_rng_expectation = expects_rng
        return expects_rng

    def __corrupt(self, text: str, *args: Any, **kwargs: Any) -> str:
        """Execute the corruption callable, injecting the RNG when required."""

        # Pass rng to underlying corruption function if it expects it.
        expects_rng = self._corruption_expects_rng()

        if expects_rng:
            corrupted = self.corruption_function(text, *args, rng=self.rng, **kwargs)
        else:
            corrupted = self.corruption_function(text, *args, **kwargs)
        return corrupted

    def corrupt(self, text: str | list[dict[str, Any]]) -> str | list[dict[str, Any]]:
        """Apply the corruption function to text or conversational transcripts."""

        if _is_transcript(text):
            transcript = [dict(turn) for turn in text]
            if transcript:
                transcript[-1]["content"] = self.__corrupt(
                    transcript[-1]["content"], **self.kwargs
                )
            return transcript

        return self.__corrupt(text, **self.kwargs)

    def corrupt_dataset(self, dataset: Dataset, columns: list[str]) -> Dataset:
        """Apply corruption lazily across dataset columns."""

        if _DatasetsDataset is None:
            message = "datasets is not installed"
            raise ModuleNotFoundError(message) from _datasets_error

        def __corrupt_row(row: dict[str, Any]) -> dict[str, Any]:
            row = dict(row)
            for column in columns:
                value = row[column]
                if _is_transcript(
                    value,
                    allow_empty=False,
                    require_all_content=True,
                ):
                    row[column] = self.corrupt(value)
                elif isinstance(value, list):
                    row[column] = [self.corrupt(item) for item in value]
                else:
                    row[column] = self.corrupt(value)
            return row

        return dataset.with_transform(__corrupt_row)

    def __call__(self, text: str, *args: Any, **kwds: Any) -> str | list[dict[str, Any]]:
        """Allow a glitchling to be invoked directly like a callable."""

        return self.corrupt(text, *args, **kwds)

    def reset_rng(self, seed: int | None = None) -> None:
        """Reset the glitchling's RNG to its initial seed."""

        if seed is not None:
            self.seed = seed
        if self.seed is not None:
            self.rng = random.Random(self.seed)

    def clone(self, seed: int | None = None) -> "Glitchling":
        """Create a copy of this glitchling, optionally with a new seed."""

        cls = self.__class__
        filtered_kwargs = {k: v for k, v in self.kwargs.items() if k != "seed"}
        clone_seed = seed if seed is not None else self.seed
        if clone_seed is not None:
            filtered_kwargs["seed"] = clone_seed

        if cls is Glitchling:
            return Glitchling(
                self.name,
                self.corruption_function,
                self.level,
                self.order,
                pipeline_operation=self._pipeline_descriptor_factory,
                **filtered_kwargs,
            )

        return cls(**filtered_kwargs)





class Gaggle(Glitchling):
    """A collection of glitchlings executed in a deterministic order."""

    def __init__(self, glitchlings: list[Glitchling], seed: int = 151):
        """Initialize the gaggle and derive per-glitchling RNG seeds.

        Args:
            glitchlings: Glitchlings to orchestrate.
            seed: Master seed used to derive per-glitchling seeds.
        """

        super().__init__("Gaggle", self.corrupt, AttackWave.DOCUMENT, seed=seed)
        self._clones_by_index: list[Glitchling] = []
        for idx, glitchling in enumerate(glitchlings):
            clone = glitchling.clone()
            setattr(clone, "_gaggle_index", idx)
            self._clones_by_index.append(clone)

        self.glitchlings: dict[AttackWave, list[Glitchling]] = {
            level: [] for level in AttackWave
        }
        self.apply_order: list[Glitchling] = []
        self._plan: list[tuple[int, int]] = []
        self.sort_glitchlings()

    @staticmethod
    def derive_seed(master_seed: int, glitchling_name: str, index: int) -> int:
        """Derive a deterministic seed for a glitchling based on the master seed."""
        def _int_to_bytes(value: int) -> bytes:
            if value == 0:
                return b"\x00"

            abs_value = abs(value)
            length = max(1, (abs_value.bit_length() + 7) // 8)

            if value < 0:
                while True:
                    try:
                        return value.to_bytes(length, "big", signed=True)
                    except OverflowError:
                        length += 1

            return abs_value.to_bytes(length, "big", signed=False)

        hasher = blake2s(digest_size=8)
        hasher.update(_int_to_bytes(master_seed))
        hasher.update(b"\x00")
        hasher.update(glitchling_name.encode("utf-8"))
        hasher.update(b"\x00")
        hasher.update(_int_to_bytes(index))
        return int.from_bytes(hasher.digest(), "big")

    def sort_glitchlings(self) -> None:
        """Sort glitchlings by wave then order to produce application order."""

        plan = _plan_glitchling_sequence(self._clones_by_index, self.seed)
        self._plan = plan

        self.glitchlings = {level: [] for level in AttackWave}
        for clone in self._clones_by_index:
            self.glitchlings[clone.level].append(clone)

        missing = set(range(len(self._clones_by_index)))
        apply_order: list[Glitchling] = []
        for index, derived_seed in plan:
            clone = self._clones_by_index[index]
            clone.reset_rng(int(derived_seed))
            apply_order.append(clone)
            missing.discard(index)

        if missing:
            missing_indices = ", ".join(str(idx) for idx in sorted(missing))
            message = f"Orchestration plan missing glitchlings at indices: {missing_indices}"
            raise RuntimeError(message)

        self.apply_order = apply_order

    @staticmethod
    def rust_pipeline_supported() -> bool:
        """Return ``True`` when the compiled Rust pipeline is importable."""

        return _compose_glitchlings_rust is not None

    @staticmethod
    def rust_pipeline_enabled() -> bool:
        """Return ``True`` when the Rust pipeline is available and not explicitly disabled."""

        return Gaggle.rust_pipeline_supported() and _pipeline_feature_flag_enabled()

    def _pipeline_descriptors(self) -> list[dict[str, Any]] | None:
        if not self.rust_pipeline_enabled():
            return None

        descriptors: list[dict[str, Any]] = []
        for glitchling in self.apply_order:
            operation = glitchling.pipeline_operation()
            if operation is None:
                return None

            seed = glitchling.seed
            if seed is None:
                index = getattr(glitchling, "_gaggle_index", None)
                master_seed = self.seed
                if index is None or master_seed is None:
                    return None
                seed = Gaggle.derive_seed(master_seed, glitchling.name, index)

            descriptors.append(
                {
                    "name": glitchling.name,
                    "operation": operation,
                    "seed": int(seed),
                }
            )

        return descriptors

    def corrupt(self, text: str) -> str:
        """Apply each glitchling to the provided text sequentially."""

        master_seed = self.seed
        descriptors = self._pipeline_descriptors()
        if master_seed is not None and descriptors is not None:
            try:
                return _compose_glitchlings_rust(text, descriptors, master_seed)
            except Exception:  # pragma: no cover - fall back to Python execution
                log.debug("Rust pipeline failed; falling back", exc_info=True)

        corrupted = text
        for glitchling in self.apply_order:
            corrupted = glitchling(corrupted)
        return corrupted
