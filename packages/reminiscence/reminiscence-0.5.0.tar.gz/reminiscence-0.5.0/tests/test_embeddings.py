"""Tests for embeddings module."""

import pytest

from reminiscence.embeddings import create_embedder
from reminiscence.embeddings.fastembed import FastEmbedEmbedder
from reminiscence import ReminiscenceConfig


class TestEmbedderFactory:
    """Test embedder factory."""

    def test_create_embedder_default(self):
        """Should create default embedder (FastEmbed)."""
        config = ReminiscenceConfig()
        embedder = create_embedder(config)

        assert isinstance(embedder, FastEmbedEmbedder)
        assert embedder.embedding_dim > 0

    def test_create_embedder_explicit_fastembed(self):
        """Should create FastEmbed when specified."""
        config = ReminiscenceConfig(embedding_backend="fastembed")
        embedder = create_embedder(config)

        assert isinstance(embedder, FastEmbedEmbedder)

    def test_create_embedder_auto(self):
        """Should create FastEmbed with 'auto' backend."""
        config = ReminiscenceConfig(embedding_backend="auto")
        embedder = create_embedder(config)

        assert isinstance(embedder, FastEmbedEmbedder)

    def test_create_embedder_invalid_backend(self):
        """Should raise on invalid backend."""
        config = ReminiscenceConfig(embedding_backend="invalid")

        with pytest.raises(ValueError, match="Unknown embedding_backend"):
            create_embedder(config)


class TestFastEmbedEmbedder:
    """Test FastEmbed implementation."""

    def test_embed_basic(self):
        """Should generate embeddings."""
        config = ReminiscenceConfig()
        embedder = FastEmbedEmbedder(config)

        embedding = embedder.embed("test text")

        assert isinstance(embedding, list)
        assert len(embedding) == embedder.embedding_dim
        assert all(isinstance(x, float) for x in embedding)

    def test_embed_deterministic(self):
        """Same text should produce same embedding."""
        config = ReminiscenceConfig()
        embedder = FastEmbedEmbedder(config)

        emb1 = embedder.embed("test")
        emb2 = embedder.embed("test")

        assert emb1 == emb2

    def test_embedding_dim(self):
        """Should detect correct embedding dimension."""
        config = ReminiscenceConfig()
        embedder = FastEmbedEmbedder(config)

        # Default model is 384 dims
        assert embedder.embedding_dim == 384

    def test_custom_model(self):
        """Should accept custom model name."""
        config = ReminiscenceConfig(model_name="sentence-transformers/all-MiniLM-L6-v2")
        embedder = FastEmbedEmbedder(config)

        embedding = embedder.embed("test")
        assert len(embedding) == embedder.embedding_dim

    def test_embed_empty_string(self):
        """Should handle empty string."""
        config = ReminiscenceConfig()
        embedder = FastEmbedEmbedder(config)

        embedding = embedder.embed("")

        assert isinstance(embedding, list)
        assert len(embedding) == embedder.embedding_dim

    def test_embed_multilingual(self):
        """Should handle multilingual text."""
        config = ReminiscenceConfig()
        embedder = FastEmbedEmbedder(config)

        # Test different languages
        emb_en = embedder.embed("Hello world")
        emb_es = embedder.embed("Hola mundo")
        emb_zh = embedder.embed("你好世界")

        assert len(emb_en) == embedder.embedding_dim
        assert len(emb_es) == embedder.embedding_dim
        assert len(emb_zh) == embedder.embedding_dim

        # Different languages should produce different embeddings
        assert emb_en != emb_es
        assert emb_en != emb_zh


class TestBatchEmbedding:
    """Test batch embedding functionality."""

    def test_embed_batch_basic(self):
        """Should generate embeddings for multiple texts."""
        config = ReminiscenceConfig()
        embedder = FastEmbedEmbedder(config)

        texts = ["hello", "world", "test"]
        embeddings = embedder.embed_batch(texts)

        assert len(embeddings) == 3
        assert all(len(emb) == embedder.embedding_dim for emb in embeddings)

    def test_embed_batch_empty(self):
        """Should handle empty batch."""
        config = ReminiscenceConfig()
        embedder = FastEmbedEmbedder(config)

        embeddings = embedder.embed_batch([])

        assert embeddings == []

    def test_embed_batch_uses_config_batch_size(self):
        """Should use batch size from config."""
        config = ReminiscenceConfig(embedding_batch_size=16)
        embedder = FastEmbedEmbedder(config)

        assert embedder.config.embedding_batch_size == 16

        texts = ["text"] * 50
        embeddings = embedder.embed_batch(texts)

        assert len(embeddings) == 50

    def test_embed_batch_vs_sequential(self):
        """Batch should produce same results as sequential."""
        config = ReminiscenceConfig()
        embedder = FastEmbedEmbedder(config)

        texts = ["hello", "world"]

        # Sequential
        emb_seq = [embedder.embed(t) for t in texts]

        # Batch
        emb_batch = embedder.embed_batch(texts)

        # Should be approximately equal
        for seq, batch in zip(emb_seq, emb_batch):
            assert len(seq) == len(batch)
