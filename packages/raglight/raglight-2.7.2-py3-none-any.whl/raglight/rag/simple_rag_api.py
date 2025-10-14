from typing import List
import shutil
import logging

from ..config.vector_store_config import VectorStoreConfig
from ..config.rag_config import RAGConfig
from ..rag.builder import Builder
from ..rag.rag import RAG
from ..vectorstore.vector_store import VectorStore
from ..models.data_source_model import DataSource, FolderSource, GitHubSource
from ..scrapper.github_scrapper import GithubScrapper


class RAGPipeline:
    """
    A class that represents a Retrieval-Augmented Generation (RAG) pipeline.

    The pipeline combines various data sources (e.g., local folders, GitHub repositories),
    embeddings, and a language model to provide context-aware answers to questions.
    """

    def __init__(
        self, config: RAGConfig, vector_store_config: VectorStoreConfig
    ) -> None:
        """
        Initializes the RAGPipeline with a knowledge base and model.

        Args:
            knowledge_base (List[DataSource]): A list of data source objects (e.g., FolderSource, GitHubSource).
            k (int, optional): The number of top documents to retrieve. Defaults to 5.
            model_name (str, optional): The name of the LLM to use. Defaults to Settings.DEFAULT_LLM.
            provider (str, optional): The name of the LLM provider you want to use : Ollama/LMStudio.
        """
        self.knowledge_base = config.knowledge_base
        self.ignore_folders = config.ignore_folders
        model_embeddings: str = vector_store_config.embedding_model
        persist_directory: str = vector_store_config.persist_directory
        collection_name: str = vector_store_config.collection_name
        system_prompt: str = config.system_prompt
        api_base: str = config.api_base
        embeddings_api_base: str = vector_store_config.api_base
        database: str = vector_store_config.database
        model_name: str = config.llm
        provider: str = config.provider
        embeddings_provider: str = vector_store_config.provider
        stream: bool = config.stream
        k: int = config.k
        self.rag: RAG = (
            Builder()
            .with_embeddings(
                embeddings_provider,
                model_name=model_embeddings,
                api_base=embeddings_api_base,
            )
            .with_vector_store(
                database,
                persist_directory=persist_directory,
                collection_name=collection_name,
                host=vector_store_config.host,
                port=vector_store_config.port,
            )
            .with_llm(
                provider,
                model_name=model_name,
                system_prompt=system_prompt,
                api_base=api_base,
            )
            .build_rag(k=k)
        )
        self.github_scrapper: GithubScrapper = GithubScrapper()

    def get_vector_store(self) -> VectorStore:
        return self.rag.vector_store

    def build(self) -> None:
        """
        Builds the RAG pipeline by ingesting data from the knowledge base.

        This method processes the data sources (e.g., folders, GitHub repositories)
        and creates the embeddings for the vector store.
        """
        repositories: List[str] = []
        if not self.knowledge_base:
            return
        for source in self.knowledge_base:
            if isinstance(source, FolderSource):
                self.get_vector_store().ingest(
                    data_path=source.path, ignore_folders=self.ignore_folders
                )
            if isinstance(source, GitHubSource):
                repositories.append(source)
        if len(repositories) > 0:
            self.ingest_github_repositories(repositories)

    def ingest_github_repositories(self, repositories: List[GitHubSource]) -> None:
        """
        Clones and processes GitHub repositories for the pipeline.

        Args:
            repositories (List[str]): A list of GitHub repository URLs to clone and ingest.
        """
        self.github_scrapper.set_repositories(repositories)
        repos_path: str = self.github_scrapper.clone_all()
        self.get_vector_store().ingest(
            data_path=repos_path, ignore_folders=self.ignore_folders
        )
        shutil.rmtree(repos_path)
        logging.info("✅ GitHub repositories cleaned successfully!")

    def generate(self, question: str) -> str:
        """
        Asks a question to the pipeline and retrieves the generated answer.

        Args:
            question (str): The question to ask the pipeline.

        Returns:
            str: The generated answer from the pipeline.
        """
        response: str = self.rag.generate(question)
        return response
