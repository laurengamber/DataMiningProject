"""Reproducible article-level BERTopic workflow; imports are lazy for audit-only use."""

from pathlib import Path
import json, platform, sys, time, hashlib
import importlib.metadata as metadata
import numpy as np
import pandas as pd

# Shared corpus/evaluation code lives in final-project/code/shared; re-exported for notebooks and tests.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from shared.corpus import (
    SEED,
    CORPUS,
    write_json,
    digest,
    corpus_hash,
    clean_text,
    audit_corpus,
    load_corpus,
)
from shared.evaluation import (
    representation_text,
    reference_texts,
    coherence,
    stability,
    jaccard_table,
    validate_classical,
    publication_exports,
    review_packets,
    summarize_reviews,
)

MODEL = "thenlper/gte-small"
MODEL_REVISION = "17e1f347d17fe144873b1201da91788898c639cd"


def token_chunks(text, tokenizer, size=480):
    ids = tokenizer.encode(text, add_special_tokens=False, verbose=False)
    if not ids:
        raise ValueError("Empty token sequence")
    chunks = [ids[i : i + size] for i in range(0, len(ids), size)]
    assert sum(map(len, chunks)) == len(ids)
    assert all(
        len(c) + tokenizer.num_special_tokens_to_add(pair=False) <= 512 for c in chunks
    )
    return chunks


def validate_embeddings(arr, n):
    if (
        arr.shape != (n, 384)
        or not np.isfinite(arr).all()
        or not np.allclose(np.linalg.norm(arr, axis=1), 1, atol=1e-4)
    ):
        raise ValueError("Invalid or misaligned embeddings")


def embed_corpus(df, root, pilot=False):
    import torch
    from sentence_transformers import SentenceTransformer

    root = Path(root)
    cache = root / "Results/modern/cache"
    cache.mkdir(parents=True, exist_ok=True)
    download_start = time.perf_counter()
    # Resolve mutable model name to an immutable revision and include it in cache identity.
    revision_path = cache / "model_revision.json"
    if revision_path.exists():
        revision = json.loads(revision_path.read_text())["revision"]
    else:
        pointer_path = root / "Results/modern/embedding_pointer.json"
        revision = (
            json.loads(pointer_path.read_text())["manifest"]["revision"]
            if pointer_path.exists()
            else MODEL_REVISION
        )
        write_json(revision_path, dict(model=MODEL, revision=revision))
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    local = (cache / "models/models--thenlper--gte-small/snapshots" / revision).exists()
    model = SentenceTransformer(
        MODEL,
        revision=revision,
        device=device,
        cache_folder=str(cache / "models"),
        local_files_only=local,
    )
    model.eval()
    download_seconds = time.perf_counter() - download_start
    manifest = dict(
        article_ids=df.article_id.astype(str).tolist(),
        text_hash=digest(df.text.tolist()),
        model=MODEL,
        revision=revision,
        chunk_tokens=480,
        pooling="token_weighted_mean_l2",
        dimension=384,
        device=device,
    )
    key = digest(manifest)
    folder = cache / key
    folder.mkdir(exist_ok=True)
    manifest_path = folder / "manifest.json"
    if manifest_path.exists() and json.loads(manifest_path.read_text()) != manifest:
        raise ValueError("Cache manifest mismatch")
    write_json(manifest_path, manifest)
    started = time.perf_counter()
    vectors = []
    diagnostics = []
    reused = 0
    for i, row in enumerate(df.itertuples()):
        path = folder / f"{i:05d}.npz"
        if path.exists():
            with np.load(path) as saved:
                v = saved["embedding"]
                counts = saved["counts"]
            validate_embeddings(v[None, :], 1)
            reused += 1
        else:
            chunks = token_chunks(row.text, model.tokenizer)
            counts = np.array(list(map(len, chunks)))
            outputs = []
            for j in range(0, len(chunks), 32):
                batch = [
                    [model.tokenizer.cls_token_id] + c + [model.tokenizer.sep_token_id]
                    for c in chunks[j : j + 32]
                ]
                width = max(map(len, batch))
                features = {
                    "input_ids": torch.tensor(
                        [
                            c + [model.tokenizer.pad_token_id] * (width - len(c))
                            for c in batch
                        ],
                        device=device,
                    ),
                    "attention_mask": torch.tensor(
                        [[1] * len(c) + [0] * (width - len(c)) for c in batch],
                        device=device,
                    ),
                }
                with torch.no_grad():
                    outputs.append(model(features)["sentence_embedding"].cpu().numpy())
            v = np.average(np.concatenate(outputs), axis=0, weights=counts)
            v = (v / np.linalg.norm(v)).astype("float32")
            validate_embeddings(v[None, :], 1)
            temp = path.with_suffix(".tmp.npz")
            np.savez(temp, embedding=v, counts=counts)
            temp.replace(path)
        vectors.append(v)
        diagnostics.append(
            dict(
                article_id=row.article_id,
                chunks=len(counts),
                tokens=int(sum(counts)),
                largest_chunk=int(max(counts)),
            )
        )
        if (i + 1) % 200 == 0:
            print(f"Embedded {i+1}/{len(df)} articles", flush=True)
    arr = np.stack(vectors)
    validate_embeddings(arr, len(df))
    pd.DataFrame(diagnostics).to_csv(folder / "chunk_diagnostics.csv", index=False)
    np.save(folder / "embeddings.npy", arr)
    timing = dict(
        hardware=platform.platform(),
        python=sys.version,
        versions={
            p: metadata.version(p)
            for p in ["torch", "sentence-transformers", "transformers", "numpy"]
        },
        model_load_download_seconds=download_seconds,
        embedding_seconds=time.perf_counter() - started,
        reused_articles=reused,
        device=device,
    )
    timing_path = folder / "timings.json"
    previous = json.loads(timing_path.read_text()) if timing_path.exists() else {}
    write_json(
        timing_path,
        dict(
            first_execution=previous.get("first_execution", previous or timing),
            latest_execution=timing,
        ),
    )
    if not pilot:
        write_json(
            root / "Results/modern/embedding_pointer.json",
            dict(
                folder=str(folder.relative_to(root)),
                manifest=manifest,
                array_hash=hashlib.sha256(arr.tobytes()).hexdigest(),
            ),
        )
    return arr, folder


def load_inputs(root, corpus=CORPUS):
    root = Path(root)
    df = load_corpus(Path(corpus).parent)
    pointer = json.loads((root / "Results/modern/embedding_pointer.json").read_text())
    m = pointer["manifest"]
    if m["article_ids"] != df.article_id.tolist() or m["text_hash"] != digest(
        df.text.tolist()
    ):
        raise ValueError("Corpus/cache mismatch")
    if (
        m["model"] != MODEL
        or m["revision"] != MODEL_REVISION
        or m["chunk_tokens"] != 480
        or m["pooling"] != "token_weighted_mean_l2"
        or m["dimension"] != 384
    ):
        raise ValueError("Embedding settings differ from the documented pipeline")
    if json.loads((root / pointer["folder"] / "manifest.json").read_text()) != m:
        raise ValueError("Embedding pointer and cache manifest disagree")
    arr = np.load(root / pointer["folder"] / "embeddings.npy")
    validate_embeddings(arr, len(df))
    if pointer.get("array_hash") != hashlib.sha256(arr.tobytes()).hexdigest():
        raise ValueError("Embedding array checksum mismatch")
    return df, arr


def term_table(model):
    return pd.DataFrame(
        [
            dict(topic_id=t, rank=i + 1, term=w, weight=float(v))
            for t in model.get_topics()
            for i, (w, v) in enumerate(model.get_topic(t))
            if w
        ]
    )


def silhouette(embeddings, labels, metric):
    from sklearn.metrics import silhouette_score

    labels = np.asarray(labels)
    indices = np.flatnonzero(labels >= 0)
    if len(indices) > 2000:
        indices = np.sort(
            np.random.default_rng(SEED).choice(indices, 2000, replace=False)
        )
    k = len(set(labels[indices]))
    if not 2 <= k < len(indices):
        return np.nan, "Undefined: fewer than two clusters or all singleton clusters"
    return (
        float(silhouette_score(embeddings[indices], labels[indices], metric=metric)),
        "ok",
    )


def evaluate(model, embeddings, texts, dictionary):
    terms = term_table(model)
    c = coherence(terms, texts, dictionary)
    labels = np.array(model.topics_)
    top = terms[(terms.topic_id >= 0) & (terms["rank"] <= 10)]
    s, reason = silhouette(embeddings, labels, "cosine")
    return (
        dict(
            topic_count=len(set(labels) - {-1}),
            outlier_fraction=float(np.mean(labels == -1)),
            coherence=float(c.coherence.mean()),
            vocabulary_coverage=float(c.vocabulary_coverage.mean()),
            keyword_diversity=top.term.nunique() / len(top) if len(top) else np.nan,
            silhouette_cosine=s,
            silhouette_status=reason,
            topic_sizes=pd.Series(labels).value_counts().to_dict(),
        ),
        c,
    )
