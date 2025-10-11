from senstore.segmenter import Segmenter
from vecstore.vecstore import VecStore
from fastembed import TextEmbedding
import networkx as nx
import os
import numpy as np


class SentEmbedder:
    """A class that embeds sentences from a text file and stores them in a vector store."""

    def __init__(
        self,
        name: str = "senstore",
        cache_dir="cache/",
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        caching=False,
    ):
        self.name = name
        self.cache_dir = cache_dir
        self.caching = caching

        self.segmenter = Segmenter()

        self.vecstore_name = f"{self.cache_dir}{name}.bin"
        self.sentfile_name = f"{self.cache_dir}{name}.tsv"
        self.dimfile_name = f"{self.cache_dir}{name}.txt"

        self.model_name = model_name
        self.batch_size = 512
        home = os.getenv("HOME")
        if home is None:
            home = "."
        self.model_dir = home + "/.cache/fastembed/"
        self.clear()

    def clear(self):
        """Clear the vector store and associated data."""
        # if os.path.exists(self.vecstore_name):
        #    os.remove(self.vecstore_name)
        self.vecstore = None
        self.sents = None
        self.ranks = None
        self.dim = -1

    def is_cleared(self) -> bool:
        """Check if the embedder is cleared."""
        return (
            self.vecstore is None
            and self.sents is None
            and self.ranks is None
            and self.dim < 0
        )

    def digest_sents(self, sents: list[str]):
        """Digest a list of sentences, embed them, and store them in the vector store."""
        assert self.is_cleared(), "Embedder is already initialized."
        self.sents = sents
        embeddings, dim = self.get_embeddings(self.sents)
        self.dim = dim
        self.store_embeddings(embeddings, dim)
        self.ranks = self.get_ranks()

    def digest_text(self, text: str):
        """Digest a text string, segment it into sentences, embed them, and store them in the vector store."""
        self.digest_sents(self.text2sents(text))

    def digest_file(self, fname: str):
        """Digest a text file, segment it into sentences, embed them, and store them in the vector store."""
        if self.caching and os.path.exists(self.vecstore_name):
            print(f"Loading cached vecstore {self.vecstore_name}")
            self.load()
            return

        with open(fname, "r") as f:
            text = f.read()
        self.digest_text(text)
        if self.caching:
            self.save()

    def digest_folder(self, folder_name: str):
        """Digest files in a folder, segment them into sentences, embed them, and store them in a shared vector store."""

        if self.caching and os.path.exists(self.vecstore_name):
            print(f"Loading cached vecstore {self.vecstore_name}")
            self.load()
            return

        sents = []
        for root, _, files in os.walk(folder_name):
            for file in files:
                if file.lower().endswith(".txt"):
                    fname = os.path.join(root, file)
                    print(f"Digesting file: {fname}")
                    with open(fname, "r") as f:
                        text = f.read()
                    new_sents = self.segmenter.text2sents(text)
                    sents.extend(new_sents)
                    print(f"Finished digesting file: {fname}")
        self.digest_sents(sents)
        if self.caching:
            self.save()

    def text2sents(self, text: str) -> list[str]:
        """Segment text into sentences and remove duplicates."""
        sents = self.segmenter.text2sents(text)
        sents = list({s: True for s in sents if s.strip()})
        return sents

    def get_embeddings(self, sents: list[str]) -> tuple[list[np.ndarray], int]:
        """Get embeddings for a list of sentences."""
        assert sents, "No sentences to embed."

        # print(f"Getting embeddings for {len(sents)} sentences...")

        embedding_model = TextEmbedding(
            self.model_name,
            cache_dir=self.model_dir,
            batch_size=self.batch_size,
            providers=["CPUExecutionProvider"],
            local_files_only=True,
        )

        embeddings = list(embedding_model.embed(sents))

        dim = embeddings[0].shape[0] if embeddings else -1

        return embeddings, dim

    def store_embeddings(self, embeddings, dim: int):
        """Store embeddings in the vector store."""
        assert self.vecstore is None, "Vector store is already initialized."
        self.vecstore = VecStore(self.vecstore_name, dim=dim)
        print(f"Vecstore created")
        self.vecstore.add(embeddings)

    def get_vecs(self) -> np.ndarray:
        """Get all vectors from the vector store."""
        assert self.vecstore is not None, "Vector store is not initialized."
        return self.vecstore.vecs(as_list=False)  # type: ignore

    def get_ids(self) -> list[int]:
        """Get all IDs from the vector store."""
        assert self.vecstore is not None, "Vector store is not initialized."
        return self.vecstore.ids()

    def hits(self, query: str, top_k: int) -> list[tuple[int, float]]:
        """Query the vector store for the top_k ids+score matches to the query."""
        # print(
        #    f"Querying vecstore {self.vecstore_name} for top {top_k} matches to: {query}"
        # )
        query_emb = self.embed_query(query)

        assert self.vecstore is not None, "Vector store is not initialized."
        matching_ids = dict(self.vecstore.query_one(query_emb[0], k=top_k))

        return list(matching_ids.items())

    def query(
        self, query: str, top_k: int
    ) -> list[tuple[str, tuple[int, float, float]]]:
        hits = self.hits(query, top_k)
        assert self.sents is not None, "Sentences are not initialized."
        assert self.ranks is not None, "Ranks are not initialized."
        res = [(self.sents[i], (int(i), float(r), self.ranks[i])) for i, r in hits]
        return res

    def query_orbit(self, query: str) -> np.ndarray:
        """Query the vector store for all matches to the query."""
        assert self.sents is not None, "Sentences are not initialized."
        res = self.hits(query, len(self.sents))
        res = sorted(res, key=lambda x: x[0])
        return np.array([np.float32(r[1]) for r in res])

    def embed_query(self, query: str) -> np.ndarray:
        """Embed a query string."""
        print(f"Embedding query: {query}")
        embs, _dim = self.get_embeddings([query])
        assert embs is not None
        return np.array(embs)

    def get_ranks(self, k=3) -> dict[int, float]:
        """Rank the sentences based on recommendations from their embeddings."""
        assert self.vecstore is not None, "Vector store is not initialized."

        # rank all the matches for how they correlate with each other
        knns = self.vecstore.all_knns(k=k, as_weights=False)

        ranked_ids = knn_graph_ranks(knns)

        return ranked_ids

    def save(self):
        """Save the vector store to disk."""
        assert self.vecstore is not None, "Vector store is not initialized."
        assert self.dim > 0, "Dimension is not set."
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        with open(self.dimfile_name, "w") as f:
            f.write(f"{self.dim}\n")
        print(f"Dimension {self.dim} saved to {self.dimfile_name}.")
        self.vecstore.save()
        print(f"Vecstore {self.vecstore_name} saved.", self.vecstore.dim, self)
        assert self.sents is not None, "Sentences are not initialized."
        assert self.ranks is not None, "Ranks are not initialized."
        with open(self.sentfile_name, "w") as f:
            for ir, s in zip(self.ranks.items(), self.sents):
                s = s.replace("\t", " ").replace("\n", " ")
                _, r = ir
                f.write(f"{r:.6f}\t{s}\n")
        print(f"Sentences {self.sentfile_name} saved.")

    def load(self):
        """Load the vector store from disk."""
        assert self.vecstore is None, "Vector store is already initialized."
        assert os.path.exists(
            self.vecstore_name
        ), f"Vector store file {self.vecstore_name} does not exist."
        assert os.path.exists(self.dimfile_name), "Dimension    file does not exist."
        with open(self.dimfile_name, "r") as f:
            self.dim = int(f.readline().strip())

        self.vecstore = VecStore(self.vecstore_name, dim=self.dim)
        self.vecstore.load()

        print(f"Vecstore {self.vecstore_name} loaded.", self.vecstore.dim)
        self.dim = self.vecstore.dim

        assert os.path.exists(self.sentfile_name), "Sentence file does not exist."
        self.sents = []
        self.ranks = dict()
        with open(self.sentfile_name, "r") as f:
            for i, line in enumerate(f):
                r, s = line.split("\t", 1)
                self.sents.append(s.strip())
                self.ranks[i] = float(r)
        print(f"Sentences {self.sentfile_name} loaded.")

    def all_computed(self) -> tuple[list[str], np.ndarray, list[float]]:
        """Get the sentences, their embeddings, and their ranks."""
        assert self.sents is not None, "Sentences are not initialized."
        assert self.vecstore is not None, "Vector store is not initialized."
        assert self.dim > 0, "Dimension is not set."
        assert len(self.sents) == len(
            self.vecstore.ids()
        ), "Mismatch between sentences and vector store IDs."
        assert self.ranks is not None, "Ranks are not initialized."
        rank_vals = list(self.ranks.values())
        assert len(rank_vals) == len(
            self.sents
        ), "Mismatch between ranks and sentences."

        # array of sents, array of vecs, array of ranks
        return self.sents, self.get_vecs(), rank_vals


def knn_graph_ranks(knns) -> dict[int, float]:
    """Return the PageRank of a graph built from a list of nearest neighbors."""
    g = nx.DiGraph()
    for i, xs in enumerate(knns):
        for x in xs:
            g.add_edge(i, x[0], weight=1 - x[1])
    rs = nx.pagerank(g)
    return rs
