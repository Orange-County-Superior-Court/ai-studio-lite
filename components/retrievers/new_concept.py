
from typing import List

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever



class CustomRetriever(BaseRetriever):
    """A toy retriever that contains the top k documents that contain the user query.

    This retriever only implements the sync method _get_relevant_documents.

    If the retriever were to involve file access or network access, it could benefit
    from a native async implementation of `_aget_relevant_documents`.

    As usual, with Runnables, there's a default async implementation that's provided
    that delegates to the sync implementation running on another thread.
    """

    documents: List[Document]
    """List of documents to retrieve from."""
    k: int
    """Number of top results to return"""

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Sync implementations for retriever."""
        matching_documents = []
        for document in documents:
            if len(matching_documents) > self.k:
                return matching_documents

            if query.lower() in document.page_content.lower():
                matching_documents.append(document)
        return matching_documents

documents = [
    Document(
        page_content="Dogs are great companions, known for their loyalty and friendliness.",
        metadata={"type": "dog", "trait": "loyalty"},
    ),
    Document(
        page_content="Cats are independent pets that often enjoy their own space.",
        metadata={"type": "cat", "trait": "independence"},
    ),
    Document(
        page_content="Goldfish are popular pets for beginners, requiring relatively simple care.",
        metadata={"type": "fish", "trait": "low maintenance"},
    ),
    Document(
        page_content="Parrots are intelligent birds capable of mimicking human speech.",
        metadata={"type": "bird", "trait": "intelligence"},
    ),
    Document(
        page_content="Rabbits are social animals that need plenty of space to hop around.",
        metadata={"type": "rabbit", "trait": "social"},
    ),
]
retriever = CustomRetriever(documents=documents, k=3)


retriever.invoke("speech")

from rank_bm25 import BM25Okapi

corpus = [
    "Hello there good man!",
    "It is quite windy in London",
    "How is the weather today?"
]

tokenized_corpus = [doc.split(" ") for doc in corpus]

bm25 = BM25Okapi(tokenized_corpus)

#save the file
import pickle
import numpy as np

# Save the bm25 object to a file
with open('bm25.pkl', 'wb') as f:
    pickle.dump(bm25, f)

# Load the bm25 object from the file
with open('bm25.pkl', 'rb') as f:
    bm25 = pickle.load(f)

query = "what is the weather?"
tokenized_query = query.split(" ")

doc_scores = bm25.get_scores(tokenized_query)

# Assuming doc_scores is a numpy array
doc_scores = np.array(doc_scores)

# Get the indices of the top n values
n = 1
top_n_indices = doc_scores.argsort()[-n:][::-1]

top_n_corpus = [corpus[i] for i in top_n_indices]


from components.retrievers.retrievers import Retrievers


def format_docs(docs):
    return "\n\n".join(f"Document Name:{doc.metadata['label_04']}\n Page Number: {doc.metadata['page']+1}\n, Document Path: {doc.metadata['document_source']}\n Content:\n{doc.page_content}\n\n" for doc in docs)

retriever = Retrievers({}).get_retriever()
docs = retriever.invoke("speech")

formatted_docs = format_docs(docs)