"""
Citation Tracking

Tracks dataset usage in research publications, counts citations,
and measures research impact.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Citation:
    """
    Research citation record

    Attributes:
        citation_id: Unique citation identifier
        dataset_id: Cited dataset ID
        paper_title: Title of citing paper
        paper_authors: List of authors
        paper_url: URL to paper
        doi: Digital Object Identifier
        publication_date: When paper was published
        venue: Journal/conference name
        citation_text: How to cite the dataset
        verified: Whether citation is verified
        added_by: User who added citation
        added_at: When citation was added
        metadata: Additional metadata
    """
    citation_id: str
    dataset_id: str
    paper_title: str
    paper_authors: List[str]
    paper_url: Optional[str] = None
    doi: Optional[str] = None
    publication_date: Optional[datetime] = None
    venue: Optional[str] = None
    citation_text: Optional[str] = None
    verified: bool = False
    added_by: Optional[str] = None
    added_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "citation_id": self.citation_id,
            "dataset_id": self.dataset_id,
            "paper_title": self.paper_title,
            "paper_authors": self.paper_authors,
            "paper_url": self.paper_url,
            "doi": self.doi,
            "publication_date": self.publication_date.isoformat() if self.publication_date else None,
            "venue": self.venue,
            "citation_text": self.citation_text,
            "verified": self.verified,
            "added_by": self.added_by,
            "added_at": self.added_at.isoformat(),
            "metadata": self.metadata
        }

    def generate_bibtex(self) -> str:
        """Generate BibTeX citation entry"""
        year = self.publication_date.year if self.publication_date else "n.d."
        authors = " and ".join(self.paper_authors)

        bibtex = f"""@article{{{self.citation_id},
  title={{{self.paper_title}}},
  author={{{authors}}},
  year={{{year}}}"""

        if self.venue:
            bibtex += f",\n  journal={{{self.venue}}}"
        if self.doi:
            bibtex += f",\n  doi={{{self.doi}}}"
        if self.paper_url:
            bibtex += f",\n  url={{{self.paper_url}}}"

        bibtex += "\n}"
        return bibtex


class CitationTracker:
    """
    Tracker for research citations

    Manages citation records, counts, and impact metrics for datasets.
    """

    def __init__(self):
        self._citations: Dict[str, Citation] = {}
        self._dataset_citations: Dict[str, List[str]] = {}  # dataset_id -> citation_ids

    def add_citation(
        self,
        dataset_id: str,
        paper_title: str,
        paper_authors: List[str],
        paper_url: Optional[str] = None,
        doi: Optional[str] = None,
        publication_date: Optional[datetime] = None,
        venue: Optional[str] = None,
        citation_text: Optional[str] = None,
        added_by: Optional[str] = None,
        **metadata
    ) -> Citation:
        """
        Add citation record

        Args:
            dataset_id: Dataset being cited
            paper_title: Title of citing paper
            paper_authors: List of authors
            paper_url: URL to paper
            doi: DOI of paper
            publication_date: Publication date
            venue: Publication venue
            citation_text: Citation text
            added_by: User adding citation
            **metadata: Additional metadata

        Returns:
            Created Citation object
        """
        import hashlib

        citation_id = hashlib.md5(
            f"{dataset_id}_{paper_title}_{datetime.utcnow()}".encode()
        ).hexdigest()[:16]

        citation = Citation(
            citation_id=citation_id,
            dataset_id=dataset_id,
            paper_title=paper_title,
            paper_authors=paper_authors,
            paper_url=paper_url,
            doi=doi,
            publication_date=publication_date,
            venue=venue,
            citation_text=citation_text,
            added_by=added_by,
            metadata=metadata
        )

        self._citations[citation_id] = citation

        # Update dataset index
        if dataset_id not in self._dataset_citations:
            self._dataset_citations[dataset_id] = []
        self._dataset_citations[dataset_id].append(citation_id)

        return citation

    def get_citation(self, citation_id: str) -> Optional[Citation]:
        """Get citation by ID"""
        return self._citations.get(citation_id)

    def verify_citation(self, citation_id: str, verified: bool = True) -> bool:
        """
        Mark citation as verified

        Args:
            citation_id: Citation identifier
            verified: Verification status

        Returns:
            True if updated
        """
        citation = self._citations.get(citation_id)
        if citation:
            citation.verified = verified
            return True
        return False

    def get_dataset_citations(
        self,
        dataset_id: str,
        verified_only: bool = False
    ) -> List[Citation]:
        """
        Get all citations for a dataset

        Args:
            dataset_id: Dataset identifier
            verified_only: Only return verified citations

        Returns:
            List of citations
        """
        citation_ids = self._dataset_citations.get(dataset_id, [])
        citations = [self._citations[cid] for cid in citation_ids if cid in self._citations]

        if verified_only:
            citations = [c for c in citations if c.verified]

        return citations

    def count_citations(
        self,
        dataset_id: str,
        verified_only: bool = False
    ) -> int:
        """
        Count citations for a dataset

        Args:
            dataset_id: Dataset identifier
            verified_only: Only count verified citations

        Returns:
            Citation count
        """
        return len(self.get_dataset_citations(dataset_id, verified_only))

    def get_citation_statistics(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get citation statistics for dataset

        Args:
            dataset_id: Dataset identifier

        Returns:
            Dictionary with citation statistics
        """
        citations = self.get_dataset_citations(dataset_id)

        if not citations:
            return {
                "dataset_id": dataset_id,
                "total_citations": 0,
                "verified_citations": 0,
                "recent_citations": 0,
                "venues": [],
                "top_authors": []
            }

        verified_count = sum(1 for c in citations if c.verified)

        # Count recent citations (last year)
        one_year_ago = datetime.utcnow().replace(year=datetime.utcnow().year - 1)
        recent_count = sum(
            1 for c in citations
            if c.publication_date and c.publication_date > one_year_ago
        )

        # Collect venues
        venues = [c.venue for c in citations if c.venue]
        venue_counts = {}
        for venue in venues:
            venue_counts[venue] = venue_counts.get(venue, 0) + 1

        # Collect authors
        all_authors = []
        for c in citations:
            all_authors.extend(c.paper_authors)
        author_counts = {}
        for author in all_authors:
            author_counts[author] = author_counts.get(author, 0) + 1

        top_authors = sorted(
            author_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            "dataset_id": dataset_id,
            "total_citations": len(citations),
            "verified_citations": verified_count,
            "recent_citations": recent_count,
            "venues": list(venue_counts.keys()),
            "top_venues": sorted(venue_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "top_authors": [{"author": a, "count": c} for a, c in top_authors]
        }

    def get_impact_metrics(self, dataset_id: str) -> Dict[str, Any]:
        """
        Calculate impact metrics for dataset

        Args:
            dataset_id: Dataset identifier

        Returns:
            Dictionary with impact metrics
        """
        citations = self.get_dataset_citations(dataset_id, verified_only=True)

        if not citations:
            return {
                "h_index": 0,
                "total_citations": 0,
                "avg_citations_per_year": 0.0,
                "impact_score": 0.0
            }

        total_citations = len(citations)

        # Calculate simple h-index (would need actual paper citation counts)
        # This is a simplified version
        h_index = min(total_citations, 10)  # Placeholder

        # Calculate average citations per year
        years = set()
        for c in citations:
            if c.publication_date:
                years.add(c.publication_date.year)

        avg_per_year = total_citations / len(years) if years else 0.0

        # Simple impact score (can be enhanced)
        impact_score = total_citations * 1.5 if len(years) > 0 else 0.0

        return {
            "h_index": h_index,
            "total_citations": total_citations,
            "years_cited": len(years),
            "avg_citations_per_year": round(avg_per_year, 2),
            "impact_score": round(impact_score, 2)
        }

    def search_citations(
        self,
        query: Optional[str] = None,
        author: Optional[str] = None,
        venue: Optional[str] = None,
        year: Optional[int] = None
    ) -> List[Citation]:
        """
        Search citations with filters

        Args:
            query: Text search in title
            author: Filter by author
            venue: Filter by venue
            year: Filter by publication year

        Returns:
            List of matching citations
        """
        results = list(self._citations.values())

        if query:
            query_lower = query.lower()
            results = [
                c for c in results
                if query_lower in c.paper_title.lower()
            ]

        if author:
            results = [
                c for c in results
                if any(author.lower() in a.lower() for a in c.paper_authors)
            ]

        if venue:
            results = [
                c for c in results
                if c.venue and venue.lower() in c.venue.lower()
            ]

        if year:
            results = [
                c for c in results
                if c.publication_date and c.publication_date.year == year
            ]

        return results

    def export_citations(
        self,
        dataset_id: str,
        format: str = "json"
    ) -> Optional[str]:
        """
        Export citations for dataset

        Args:
            dataset_id: Dataset identifier
            format: Export format (json, bibtex)

        Returns:
            Serialized citations or None
        """
        citations = self.get_dataset_citations(dataset_id)

        if not citations:
            return None

        if format == "json":
            data = {
                "dataset_id": dataset_id,
                "citation_count": len(citations),
                "citations": [c.to_dict() for c in citations],
                "statistics": self.get_citation_statistics(dataset_id)
            }
            return json.dumps(data, indent=2)

        elif format == "bibtex":
            bibtex_entries = [c.generate_bibtex() for c in citations]
            return "\n\n".join(bibtex_entries)

        else:
            raise ValueError(f"Unsupported format: {format}")

    def delete_citation(self, citation_id: str) -> bool:
        """Delete citation"""
        citation = self._citations.get(citation_id)
        if citation:
            dataset_id = citation.dataset_id
            if dataset_id in self._dataset_citations:
                self._dataset_citations[dataset_id].remove(citation_id)

            del self._citations[citation_id]
            return True
        return False

    def bulk_import_citations(
        self,
        dataset_id: str,
        citations_data: List[Dict[str, Any]]
    ) -> int:
        """
        Bulk import citations

        Args:
            dataset_id: Dataset identifier
            citations_data: List of citation dictionaries

        Returns:
            Number of citations imported
        """
        count = 0
        for data in citations_data:
            try:
                pub_date = None
                if "publication_date" in data:
                    if isinstance(data["publication_date"], str):
                        pub_date = datetime.fromisoformat(data["publication_date"])
                    else:
                        pub_date = data["publication_date"]

                self.add_citation(
                    dataset_id=dataset_id,
                    paper_title=data["paper_title"],
                    paper_authors=data["paper_authors"],
                    paper_url=data.get("paper_url"),
                    doi=data.get("doi"),
                    publication_date=pub_date,
                    venue=data.get("venue"),
                    citation_text=data.get("citation_text")
                )
                count += 1
            except Exception:
                continue

        return count
