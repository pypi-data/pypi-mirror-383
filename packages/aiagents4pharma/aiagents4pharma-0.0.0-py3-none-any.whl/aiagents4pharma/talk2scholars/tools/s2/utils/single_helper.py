#!/usr/bin/env python3

"""
Utility for fetching recommendations based on a single paper.
"""

import logging
from typing import Any

import hydra
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SinglePaperRecData:
    """Helper class to organize single paper recommendation data."""

    def __init__(
        self,
        paper_id: str,
        limit: int,
        year: str | None,
        tool_call_id: str,
    ):
        self.paper_id = paper_id
        self.limit = limit
        self.year = year
        self.tool_call_id = tool_call_id
        self.cfg = self._load_config()
        self.endpoint = f"{self.cfg.api_endpoint}/{paper_id}"
        self.params = self._create_params()
        self.response = None
        self.data = None
        self.recommendations = []
        self.filtered_papers = {}
        self.content = ""

    def _load_config(self) -> Any:
        """Load hydra configuration."""
        with hydra.initialize(version_base=None, config_path="../../../configs"):
            cfg = hydra.compose(
                config_name="config",
                overrides=["tools/single_paper_recommendation=default"],
            )
            logger.info("Loaded configuration for single paper recommendation tool")
            return cfg.tools.single_paper_recommendation

    def _create_params(self) -> dict[str, Any]:
        """Create parameters for the API request."""
        params = {
            "limit": min(self.limit, 500),  # Max 500 per API docs
            "fields": ",".join(self.cfg.api_fields),
            "from": self.cfg.recommendation_params.from_pool,
        }
        if self.year:
            params["year"] = self.year
        return params

    def _fetch_recommendations(self) -> None:
        """Fetch recommendations from Semantic Scholar API."""
        logger.info(
            "Starting single paper recommendations search with paper ID: %s",
            self.paper_id,
        )

        # Wrap API call in try/except to catch connectivity issues and check response format
        for attempt in range(10):
            try:
                self.response = requests.get(
                    self.endpoint, params=self.params, timeout=self.cfg.request_timeout
                )
                self.response.raise_for_status()  # Raises HTTPError for bad responses
                break  # Exit loop if request is successful
            except requests.exceptions.RequestException as e:
                logger.error(
                    "Attempt %d: Failed to connect to Semantic Scholar API for recommendations: %s",
                    attempt + 1,
                    e,
                )
                if attempt == 9:  # Last attempt
                    raise RuntimeError(
                        "Failed to connect to Semantic Scholar API after 10 attempts."
                        "Please retry the same query."
                    ) from e

        if self.response is None:
            raise RuntimeError("Failed to obtain a response from the Semantic Scholar API.")

        logger.info(
            "API Response Status for recommendations of paper %s: %s",
            self.paper_id,
            self.response.status_code,
        )
        logger.info("Request params: %s", self.params)

        self.data = self.response.json()

        # Check for expected data format
        if "recommendedPapers" not in self.data:
            logger.error("Unexpected API response format: %s", self.data)
            raise RuntimeError(
                "Unexpected response from Semantic Scholar API. The results could not be "
                "retrieved due to an unexpected format. "
                "Please modify your search query and try again."
            )

        self.recommendations = self.data.get("recommendedPapers", [])
        if not self.recommendations:
            logger.error("No recommendations returned from API for paper: %s", self.paper_id)
            raise RuntimeError(
                "No recommendations were found for your query. Consider refining your search "
                "by using more specific keywords or different terms."
            )

    def _filter_papers(self) -> None:
        """Filter and format papers."""
        # Build filtered recommendations with unified paper_ids
        filtered: dict[str, Any] = {}
        for paper in self.recommendations:
            if not paper.get("title") or not paper.get("authors"):
                continue
            ext = paper.get("externalIds", {}) or {}
            ids: list[str] = []
            arxiv = ext.get("ArXiv")
            if arxiv:
                ids.append(f"arxiv:{arxiv}")
            pubmed = ext.get("PubMed")
            if pubmed:
                ids.append(f"pubmed:{pubmed}")
            pmc = ext.get("PubMedCentral")
            if pmc:
                ids.append(f"pmc:{pmc}")
            doi_id = ext.get("DOI")
            if doi_id:
                ids.append(f"doi:{doi_id}")
            metadata = {
                "semantic_scholar_paper_id": paper["paperId"],
                "Title": paper.get("title", "N/A"),
                "Abstract": paper.get("abstract", "N/A"),
                "Year": paper.get("year", "N/A"),
                "Publication Date": paper.get("publicationDate", "N/A"),
                "Venue": paper.get("venue", "N/A"),
                "Journal Name": (paper.get("journal") or {}).get("name", "N/A"),
                "Citation Count": paper.get("citationCount", "N/A"),
                "Authors": [
                    f"{author.get('name', 'N/A')} (ID: {author.get('authorId', 'N/A')})"
                    for author in paper.get("authors", [])
                ],
                "URL": paper.get("url", "N/A"),
                "arxiv_id": arxiv or "N/A",
                "pm_id": pubmed or "N/A",
                "pmc_id": pmc or "N/A",
                "doi": doi_id or "N/A",
                "paper_ids": ids,
                "source": "semantic_scholar",
            }
            filtered[paper["paperId"]] = metadata
        self.filtered_papers = filtered

        logger.info("Filtered %d papers", len(self.filtered_papers))

    def _get_snippet(self, abstract: str) -> str:
        """Extract the first one or two sentences from an abstract."""
        if not abstract or abstract == "N/A":
            return ""
        sentences = abstract.split(". ")
        snippet_sentences = sentences[:2]
        snippet = ". ".join(snippet_sentences)
        if not snippet.endswith("."):
            snippet += "."
        return snippet

    def _create_content(self) -> None:
        """Create the content message for the response."""
        top_papers = list(self.filtered_papers.values())[:3]
        entries: list[str] = []
        for i, paper in enumerate(top_papers):
            title = paper.get("Title", "N/A")
            year = paper.get("Year", "N/A")
            snippet = self._get_snippet(paper.get("Abstract", ""))
            entry = f"{i + 1}. {title} ({year})"
            if snippet:
                entry += f"\n   Abstract snippet: {snippet}"
            entries.append(entry)
        top_papers_info = "\n".join(entries)

        self.content = (
            "Recommendations based on the single paper were successful. "
            "Papers are attached as an artifact. "
            "Here is a summary of the recommendations:\n"
        )
        self.content += f"Number of recommended papers found: {self.get_paper_count()}\n"
        self.content += f"Query Paper ID: {self.paper_id}\n"
        self.content += "Here are a few of these papers:\n" + top_papers_info

    def process_recommendations(self) -> dict[str, Any]:
        """Process the recommendations request and return results."""
        self._fetch_recommendations()
        self._filter_papers()
        self._create_content()

        return {
            "papers": self.filtered_papers,
            "content": self.content,
        }

    def get_paper_count(self) -> int:
        """Get the number of recommended papers.

        Returns:
            int: The number of papers in the filtered papers dictionary.
        """
        return len(self.filtered_papers)
