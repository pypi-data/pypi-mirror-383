from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from glitchlings.lexicon.graph import GraphLexicon
from glitchlings.lexicon.vector import VectorLexicon


@pytest.fixture()
def vector_embeddings() -> dict[str, list[float]]:
    return {
        "alpha": [1.0, 0.0],
        "beta": [0.9, 0.1],
        "gamma": [0.0, 1.0],
        "delta": [-1.0, 0.0],
    }


@pytest.fixture()
def numberbatch_embeddings() -> dict[str, list[float]]:
    return {
        "/c/en/alpha": [1.0, 0.0],
        "/c/en/beta": [0.9, 0.1],
        "/c/en/gamma": [0.1, 0.9],
        "/c/en/delta": [-1.0, 0.0],
        "/c/es/alpha": [1.0, 0.0],
    }


@pytest.mark.parametrize("backend_name", ["vector", "graph"])
def test_backend_cache_roundtrip(
    tmp_path: Path,
    backend_name: str,
    vector_embeddings: dict[str, list[float]],
    numberbatch_embeddings: dict[str, list[float]],
) -> None:
    if backend_name == "vector":
        backend_cls: type[Any] = VectorLexicon
        kwargs: dict[str, Any] = {
            "source": vector_embeddings,
            "max_neighbors": 2,
            "min_similarity": 0.05,
        }
        restore_kwargs: dict[str, Any] = {"source": None}
    else:
        backend_cls = GraphLexicon
        kwargs = {
            "source": numberbatch_embeddings,
            "max_neighbors": 2,
            "languages": ("en",),
        }
        restore_kwargs = {"source": {}}

    word = "alpha"
    cache_path = tmp_path / f"{backend_name}_cache.json"
    lexicon = backend_cls(cache_path=cache_path, **kwargs)
    lexicon.precompute(word)
    saved_path = lexicon.save_cache()
    snapshot = backend_cls.load_cache(saved_path)
    assert snapshot.entries  # cache contains data
    assert snapshot.checksum is not None
    restored = backend_cls(cache_path=saved_path, **restore_kwargs)
    assert restored.get_synonyms(word, n=2) == lexicon.get_synonyms(word, n=2)


def test_cache_checksum_verification(tmp_path: Path, vector_embeddings: dict[str, list[float]]) -> None:
    cache_path = tmp_path / "vector_cache.json"
    lexicon = VectorLexicon(source=vector_embeddings, max_neighbors=2, min_similarity=0.05)
    lexicon.precompute("alpha")
    lexicon.save_cache(cache_path)

    with cache_path.open("r", encoding="utf8") as handle:
        payload = json.load(handle)

    payload["entries"]["alpha"].append("corrupt")  # type: ignore[index]

    with cache_path.open("w", encoding="utf8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)

    with pytest.raises(RuntimeError):
        VectorLexicon.load_cache(cache_path)
