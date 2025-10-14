#!/usr/bin/env python3
"""
Unified Guideline Tools
Consolidated clinical guidelines search tools from multiple sources.
"""

import requests
import time
import re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from .base_tool import BaseTool
from .tool_registry import register_tool


@register_tool()
class NICEWebScrapingTool(BaseTool):
    """
    Real NICE guidelines search using web scraping.
    Makes actual HTTP requests to NICE website and parses HTML responses.
    """

    def __init__(self, tool_config):
        super().__init__(tool_config)
        self.base_url = "https://www.nice.org.uk"
        self.search_url = f"{self.base_url}/search"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

    def run(self, arguments):
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)

        if not query:
            return {"error": "Query parameter is required"}

        return self._search_nice_guidelines_real(query, limit)

    def _fetch_guideline_summary(self, url):
        """Fetch summary from a guideline detail page."""
        try:
            time.sleep(0.5)  # Be respectful
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # Try to find overview section
            overview = soup.find("div", {"class": "chapter-overview"})
            if overview:
                paragraphs = overview.find_all("p")
                if paragraphs:
                    return " ".join([p.get_text().strip() for p in paragraphs[:2]])

            # Try meta description
            meta_desc = soup.find("meta", {"name": "description"})
            if meta_desc and meta_desc.get("content"):
                return meta_desc.get("content")

            # Try first paragraph in main content
            main_content = soup.find("div", {"class": "content"}) or soup.find("main")
            if main_content:
                first_p = main_content.find("p")
                if first_p:
                    return first_p.get_text().strip()

            return ""
        except Exception:
            return ""

    def _search_nice_guidelines_real(self, query, limit):
        """Search NICE guidelines using real web scraping."""
        try:
            # Add delay to be respectful
            time.sleep(1)

            params = {"q": query, "type": "guidance"}

            response = self.session.get(self.search_url, params=params, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Find the JSON data in the script tag
            script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
            if not script_tag:
                return {
                    "error": "No search results found",
                    "suggestion": "Try different search terms or check if the NICE website is accessible",
                }

            # Parse the JSON data
            import json

            try:
                data = json.loads(script_tag.string)
                documents = (
                    data.get("props", {})
                    .get("pageProps", {})
                    .get("results", {})
                    .get("documents", [])
                )
            except (json.JSONDecodeError, KeyError) as e:
                return {
                    "error": f"Failed to parse search results: {str(e)}",
                    "source": "NICE",
                }

            if not documents:
                return {
                    "error": "No NICE guidelines found",
                    "suggestion": "Try different search terms or check if the NICE website is accessible",
                }

            # Process the documents
            results = []
            for doc in documents[:limit]:
                try:
                    title = doc.get("title", "").replace("<b>", "").replace("</b>", "")
                    url = doc.get("url", "")

                    # Make URL absolute
                    if url.startswith("/"):
                        url = self.base_url + url

                    # Extract summary - try multiple fields
                    summary = (
                        doc.get("abstract", "")
                        or doc.get("staticAbstract", "")
                        or doc.get("metaDescription", "")
                        or doc.get("teaser", "")
                        or ""
                    )

                    # If still no summary, try to fetch from the detail page
                    if not summary and url:
                        summary = self._fetch_guideline_summary(url)

                    # Extract date
                    publication_date = doc.get("publicationDate", "")
                    last_updated = doc.get("lastUpdated", "")
                    date = last_updated or publication_date

                    # Extract type/category
                    nice_result_type = doc.get("niceResultType", "")
                    nice_guidance_type = doc.get("niceGuidanceType", [])
                    guideline_type = nice_result_type or (
                        nice_guidance_type[0]
                        if nice_guidance_type
                        else "NICE Guideline"
                    )

                    # Determine if it's a guideline
                    is_guideline = any(
                        keyword in guideline_type.lower()
                        for keyword in [
                            "guideline",
                            "quality standard",
                            "technology appraisal",
                        ]
                    )

                    # Extract category
                    category = "Clinical Guidelines"
                    if "quality standard" in guideline_type.lower():
                        category = "Quality Standards"
                    elif "technology appraisal" in guideline_type.lower():
                        category = "Technology Appraisal"

                    result = {
                        "title": title,
                        "url": url,
                        "summary": summary,
                        "date": date,
                        "type": guideline_type,
                        "source": "NICE",
                        "is_guideline": is_guideline,
                        "category": category,
                    }

                    results.append(result)

                except Exception:
                    # Skip items that can't be parsed
                    continue

            if not results:
                return {
                    "error": "No NICE guidelines found",
                    "suggestion": "Try different search terms or check if the NICE website is accessible",
                }

            return results

        except requests.exceptions.RequestException as e:
            return {
                "error": f"Failed to search NICE guidelines: {str(e)}",
                "source": "NICE",
            }
        except Exception as e:
            return {"error": f"Error parsing NICE response: {str(e)}", "source": "NICE"}


@register_tool()
class PubMedGuidelinesTool(BaseTool):
    """
    Search PubMed for clinical practice guidelines.
    Uses NCBI E-utilities with guideline publication type filter.
    """

    def __init__(self, tool_config):
        super().__init__(tool_config)
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.session = requests.Session()

    def run(self, arguments):
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)
        api_key = arguments.get("api_key", "")

        if not query:
            return {"error": "Query parameter is required"}

        return self._search_pubmed_guidelines(query, limit, api_key)

    def _search_pubmed_guidelines(self, query, limit, api_key):
        """Search PubMed for guideline publications."""
        try:
            # Add guideline publication type filter
            guideline_query = f"{query} AND (guideline[Publication Type] OR practice guideline[Publication Type])"

            # Search for PMIDs
            search_params = {
                "db": "pubmed",
                "term": guideline_query,
                "retmode": "json",
                "retmax": limit,
            }
            if api_key:
                search_params["api_key"] = api_key

            search_response = self.session.get(
                f"{self.base_url}/esearch.fcgi", params=search_params, timeout=30
            )
            search_response.raise_for_status()
            search_data = search_response.json()

            pmids = search_data.get("esearchresult", {}).get("idlist", [])
            search_data.get("esearchresult", {}).get("count", "0")

            if not pmids:
                return []

            # Get details for PMIDs
            time.sleep(0.5)  # Be respectful with API calls

            detail_params = {"db": "pubmed", "id": ",".join(pmids), "retmode": "json"}
            if api_key:
                detail_params["api_key"] = api_key

            detail_response = self.session.get(
                f"{self.base_url}/esummary.fcgi", params=detail_params, timeout=30
            )
            detail_response.raise_for_status()
            detail_data = detail_response.json()

            # Fetch abstracts using efetch
            time.sleep(0.5)
            abstract_params = {
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "xml",
                "rettype": "abstract",
            }
            if api_key:
                abstract_params["api_key"] = api_key

            abstract_response = self.session.get(
                f"{self.base_url}/efetch.fcgi", params=abstract_params, timeout=30
            )
            abstract_response.raise_for_status()

            # Parse abstracts from XML
            import re

            abstracts = {}
            xml_text = abstract_response.text
            # Extract abstracts for each PMID
            for pmid in pmids:
                # Find abstract text for this PMID
                pmid_pattern = rf"<PMID[^>]*>{pmid}</PMID>.*?<AbstractText[^>]*>(.*?)</AbstractText>"
                abstract_match = re.search(pmid_pattern, xml_text, re.DOTALL)
                if abstract_match:
                    # Clean HTML tags from abstract
                    abstract = re.sub(r"<[^>]+>", "", abstract_match.group(1))
                    abstracts[pmid] = abstract.strip()
                else:
                    abstracts[pmid] = ""

            # Process results
            results = []
            for pmid in pmids:
                if pmid in detail_data.get("result", {}):
                    article = detail_data["result"][pmid]

                    # Extract author information
                    authors = []
                    for author in article.get("authors", [])[:3]:
                        authors.append(author.get("name", ""))
                    author_str = ", ".join(authors)
                    if len(article.get("authors", [])) > 3:
                        author_str += ", et al."

                    # Check publication types
                    pub_types = article.get("pubtype", [])
                    is_guideline = any("guideline" in pt.lower() for pt in pub_types)

                    result = {
                        "pmid": pmid,
                        "title": article.get("title", ""),
                        "abstract": abstracts.get(pmid, ""),
                        "authors": author_str,
                        "journal": article.get("source", ""),
                        "publication_date": article.get("pubdate", ""),
                        "publication_types": pub_types,
                        "is_guideline": is_guideline,
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        "doi": (
                            article.get("elocationid", "").replace("doi: ", "")
                            if "doi:" in article.get("elocationid", "")
                            else ""
                        ),
                        "source": "PubMed",
                    }

                    results.append(result)

            return results

        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to search PubMed: {str(e)}", "source": "PubMed"}
        except Exception as e:
            return {
                "error": f"Error processing PubMed response: {str(e)}",
                "source": "PubMed",
            }


@register_tool()
class EuropePMCGuidelinesTool(BaseTool):
    """
    Search Europe PMC for clinical guidelines.
    Europe PMC provides access to life science literature including guidelines.
    """

    def __init__(self, tool_config):
        super().__init__(tool_config)
        self.base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        self.session = requests.Session()

    def run(self, arguments):
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)

        if not query:
            return {"error": "Query parameter is required"}

        return self._search_europepmc_guidelines(query, limit)

    def _search_europepmc_guidelines(self, query, limit):
        """Search Europe PMC for guideline publications."""
        try:
            # Add guideline filter to query
            guideline_query = f"guideline AND {query}"

            params = {"query": guideline_query, "format": "json", "pageSize": limit}

            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            data.get("hitCount", 0)
            results_list = data.get("resultList", {}).get("result", [])

            if not results_list:
                return []

            # Process results
            results = []
            for result in results_list:
                title = result.get("title", "")
                pub_type = result.get("pubType", "")
                abstract = result.get("abstractText", "")

                # Determine if it's a guideline
                is_guideline = (
                    "guideline" in title.lower()
                    or "guideline" in pub_type.lower()
                    or "guideline" in abstract.lower()
                )

                # Build URL
                pmid = result.get("pmid", "")
                pmcid = result.get("pmcid", "")
                doi = result.get("doi", "")

                url = ""
                if pmid:
                    url = f"https://europepmc.org/article/MED/{pmid}"
                elif pmcid:
                    url = f"https://europepmc.org/article/{pmcid}"
                elif doi:
                    url = f"https://doi.org/{doi}"

                guideline_result = {
                    "title": title,
                    "pmid": pmid,
                    "pmcid": pmcid,
                    "doi": doi,
                    "authors": result.get("authorString", ""),
                    "journal": result.get("journalTitle", ""),
                    "publication_date": result.get("firstPublicationDate", ""),
                    "publication_type": pub_type,
                    "abstract": (
                        abstract[:500] + "..." if len(abstract) > 500 else abstract
                    ),
                    "is_guideline": is_guideline,
                    "url": url,
                    "source": "Europe PMC",
                }

                results.append(guideline_result)

            return results

        except requests.exceptions.RequestException as e:
            return {
                "error": f"Failed to search Europe PMC: {str(e)}",
                "source": "Europe PMC",
            }
        except Exception as e:
            return {
                "error": f"Error processing Europe PMC response: {str(e)}",
                "source": "Europe PMC",
            }


@register_tool()
class TRIPDatabaseTool(BaseTool):
    """
    Search TRIP Database (Turning Research into Practice).
    Specialized evidence-based medicine database with clinical guidelines filter.
    """

    def __init__(self, tool_config):
        super().__init__(tool_config)
        self.base_url = "https://www.tripdatabase.com/api/search"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )

    def run(self, arguments):
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)
        search_type = arguments.get("search_type", "guideline")

        if not query:
            return {"error": "Query parameter is required"}

        return self._search_trip_database(query, limit, search_type)

    def _search_trip_database(self, query, limit, search_type):
        """Search TRIP Database for clinical guidelines."""
        try:
            params = {"criteria": query, "searchType": search_type, "limit": limit}

            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            # Parse XML response
            root = ET.fromstring(response.content)

            total = root.find("total")
            count = root.find("count")

            int(total.text) if total is not None else 0
            int(count.text) if count is not None else 0

            documents = root.findall("document")

            if not documents:
                return []

            # Process results
            results = []
            for doc in documents[:limit]:
                title_elem = doc.find("title")
                link_elem = doc.find("link")
                publication_elem = doc.find("publication")
                category_elem = doc.find("category")
                description_elem = doc.find("description")

                guideline_result = {
                    "title": title_elem.text if title_elem is not None else "",
                    "url": link_elem.text if link_elem is not None else "",
                    "description": (
                        description_elem.text if description_elem is not None else ""
                    ),
                    "publication": (
                        publication_elem.text if publication_elem is not None else ""
                    ),
                    "category": category_elem.text if category_elem is not None else "",
                    "is_guideline": True,  # TRIP returns filtered results
                    "source": "TRIP Database",
                }

                results.append(guideline_result)

            return results

        except requests.exceptions.RequestException as e:
            return {
                "error": f"Failed to search TRIP Database: {str(e)}",
                "source": "TRIP Database",
            }
        except ET.ParseError as e:
            return {
                "error": f"Failed to parse TRIP Database response: {str(e)}",
                "source": "TRIP Database",
            }
        except Exception as e:
            return {
                "error": f"Error processing TRIP Database response: {str(e)}",
                "source": "TRIP Database",
            }


@register_tool()
class WHOGuidelinesTool(BaseTool):
    """
    WHO (World Health Organization) Guidelines Search Tool.
    Searches WHO official guidelines from their publications website.
    """

    def __init__(self, tool_config):
        super().__init__(tool_config)
        self.base_url = "https://www.who.int"
        self.guidelines_url = f"{self.base_url}/publications/who-guidelines"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def run(self, arguments):
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)

        if not query:
            return {"error": "Query parameter is required"}

        return self._search_who_guidelines(query, limit)

    def _fetch_guideline_description(self, url):
        """Fetch description from a WHO guideline detail page."""
        try:
            time.sleep(0.5)  # Be respectful
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # Try to find overview or description
            overview = soup.find("div", {"class": "overview"}) or soup.find(
                "div", {"class": "description"}
            )
            if overview:
                paragraphs = overview.find_all("p")
                if paragraphs:
                    return " ".join([p.get_text().strip() for p in paragraphs[:2]])

            # Try meta description
            meta_desc = soup.find("meta", {"name": "description"}) or soup.find(
                "meta", {"property": "og:description"}
            )
            if meta_desc and meta_desc.get("content"):
                return meta_desc.get("content")

            # Try first few paragraphs in main content
            main_content = (
                soup.find("div", {"class": "content"})
                or soup.find("main")
                or soup.find("article")
            )
            if main_content:
                paragraphs = main_content.find_all("p", recursive=True)
                if paragraphs:
                    text_parts = []
                    for p in paragraphs[:3]:
                        text = p.get_text().strip()
                        if len(text) > 30:  # Skip very short paragraphs
                            text_parts.append(text)
                        if len(" ".join(text_parts)) > 300:  # Limit total length
                            break
                    if text_parts:
                        return " ".join(text_parts)

            return ""
        except Exception:
            return ""

    def _search_who_guidelines(self, query, limit):
        """Search WHO guidelines by scraping their official website."""
        try:
            # Add delay to be respectful
            time.sleep(1)

            # First, get the guidelines page
            response = self.session.get(self.guidelines_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Find all publication links
            all_links = soup.find_all("a", href=True)
            guidelines = []

            query_lower = query.lower()

            for link in all_links:
                href = link["href"]
                text = link.get_text().strip()

                # Filter for actual guideline publications
                if (
                    ("/publications/i/item/" in href or "/publications/m/item/" in href)
                    and text
                    and len(text) > 10
                ):
                    # Check if query matches the title
                    if query_lower in text.lower():
                        full_url = (
                            href if href.startswith("http") else self.base_url + href
                        )

                        # Avoid duplicates
                        if not any(g["url"] == full_url for g in guidelines):
                            # Fetch description from detail page
                            description = self._fetch_guideline_description(full_url)

                            guidelines.append(
                                {
                                    "title": text,
                                    "url": full_url,
                                    "description": description,
                                    "source": "WHO",
                                    "organization": "World Health Organization",
                                    "is_guideline": True,
                                    "official": True,
                                }
                            )

                            if len(guidelines) >= limit:
                                break

            # If no results with strict matching, get all WHO guidelines from page
            if len(guidelines) == 0:
                print(
                    f"No exact matches for '{query}', retrieving latest WHO guidelines..."
                )

                all_guidelines = []
                for link in all_links:
                    href = link["href"]
                    text = link.get_text().strip()

                    if (
                        (
                            "/publications/i/item/" in href
                            or "/publications/m/item/" in href
                        )
                        and text
                        and len(text) > 10
                    ):
                        full_url = (
                            href if href.startswith("http") else self.base_url + href
                        )

                        if not any(g["url"] == full_url for g in all_guidelines):
                            # Fetch description from detail page
                            description = self._fetch_guideline_description(full_url)

                            all_guidelines.append(
                                {
                                    "title": text,
                                    "url": full_url,
                                    "description": description,
                                    "source": "WHO",
                                    "organization": "World Health Organization",
                                    "is_guideline": True,
                                    "official": True,
                                }
                            )

                guidelines = all_guidelines[:limit]

            return guidelines

        except requests.exceptions.RequestException as e:
            return {
                "error": f"Failed to access WHO guidelines: {str(e)}",
                "source": "WHO",
            }
        except Exception as e:
            return {
                "error": f"Error processing WHO guidelines: {str(e)}",
                "source": "WHO",
            }


@register_tool()
class OpenAlexGuidelinesTool(BaseTool):
    """
    OpenAlex Guidelines Search Tool.
    Specialized tool for searching clinical practice guidelines using OpenAlex API.
    """

    def __init__(self, tool_config):
        super().__init__(tool_config)
        self.base_url = "https://api.openalex.org/works"

    def run(self, arguments):
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)
        year_from = arguments.get("year_from", None)
        year_to = arguments.get("year_to", None)

        if not query:
            return {"error": "Query parameter is required"}

        return self._search_openalex_guidelines(query, limit, year_from, year_to)

    def _search_openalex_guidelines(self, query, limit, year_from=None, year_to=None):
        """Search for clinical guidelines using OpenAlex API."""
        try:
            # Build search query to focus on guidelines
            search_query = f"{query} clinical practice guideline"

            # Build parameters
            params = {
                "search": search_query,
                "per_page": min(limit, 50),
                "sort": "cited_by_count:desc",  # Sort by citations
            }

            # Add year filters
            filters = []
            if year_from and year_to:
                filters.append(f"publication_year:{year_from}-{year_to}")
            elif year_from:
                filters.append(f"from_publication_date:{year_from}-01-01")
            elif year_to:
                filters.append(f"to_publication_date:{year_to}-12-31")

            # Filter for articles
            filters.append("type:article")

            if filters:
                params["filter"] = ",".join(filters)

            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])
            data.get("meta", {})

            guidelines = []
            for work in results:
                # Extract information
                title = work.get("title", "N/A")
                year = work.get("publication_year", "N/A")
                doi = work.get("doi", "")
                openalex_id = work.get("id", "")
                cited_by = work.get("cited_by_count", 0)

                # Extract authors
                authors = []
                authorships = work.get("authorships", [])
                for authorship in authorships[:5]:
                    author = authorship.get("author", {})
                    author_name = author.get("display_name", "")
                    if author_name:
                        authors.append(author_name)

                # Extract institutions
                institutions = []
                for authorship in authorships[:3]:
                    for inst in authorship.get("institutions", []):
                        inst_name = inst.get("display_name", "")
                        if inst_name and inst_name not in institutions:
                            institutions.append(inst_name)

                # Extract abstract
                abstract_inverted = work.get("abstract_inverted_index", {})
                abstract = (
                    self._reconstruct_abstract(abstract_inverted)
                    if abstract_inverted
                    else None
                )

                # Check if it's likely a guideline
                is_guideline = any(
                    keyword in title.lower()
                    for keyword in [
                        "guideline",
                        "recommendation",
                        "consensus",
                        "practice",
                        "statement",
                    ]
                )

                # Build URL
                url = (
                    doi
                    if doi and doi.startswith("http")
                    else (
                        f"https://doi.org/{doi.replace('https://doi.org/', '')}"
                        if doi
                        else openalex_id
                    )
                )

                guideline = {
                    "title": title,
                    "authors": authors,
                    "institutions": institutions[:3],
                    "year": year,
                    "doi": doi,
                    "url": url,
                    "openalex_id": openalex_id,
                    "cited_by_count": cited_by,
                    "is_guideline": is_guideline,
                    "source": "OpenAlex",
                    "abstract": (
                        abstract[:500] if abstract else None
                    ),  # Limit abstract length
                }

                guidelines.append(guideline)

            return guidelines

        except requests.exceptions.RequestException as e:
            return {
                "error": f"Failed to search OpenAlex: {str(e)}",
                "source": "OpenAlex",
            }
        except Exception as e:
            return {
                "error": f"Error processing OpenAlex response: {str(e)}",
                "source": "OpenAlex",
            }

    def _reconstruct_abstract(self, abstract_inverted_index):
        """Reconstruct abstract from inverted index."""
        if not abstract_inverted_index:
            return None

        try:
            # Create a list to hold words at their positions
            max_position = max(
                max(positions) for positions in abstract_inverted_index.values()
            )
            words = [""] * (max_position + 1)

            # Place each word at its positions
            for word, positions in abstract_inverted_index.items():
                for pos in positions:
                    words[pos] = word

            # Join words to form abstract
            abstract = " ".join(words).strip()
            return abstract

        except Exception:
            return None


@register_tool()
class NICEGuidelineFullTextTool(BaseTool):
    """
    Fetch full text content from NICE guideline pages.
    Takes a NICE guideline URL and extracts the complete guideline content.
    """

    def __init__(self, tool_config):
        super().__init__(tool_config)
        self.base_url = "https://www.nice.org.uk"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def run(self, arguments):
        url = arguments.get("url", "")

        if not url:
            return {"error": "URL parameter is required"}

        # Ensure it's a NICE URL
        if "nice.org.uk" not in url:
            return {"error": "URL must be a NICE guideline URL (nice.org.uk)"}

        return self._fetch_full_guideline(url)

    def _fetch_full_guideline(self, url):
        """Fetch complete guideline content from NICE page."""
        try:
            time.sleep(1)  # Be respectful
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract title
            title_elem = soup.find("h1") or soup.find("title")
            title = title_elem.get_text().strip() if title_elem else "Unknown Title"

            # Extract guideline metadata
            metadata = {}

            # Published date
            date_elem = soup.find("time") or soup.find(
                "span", {"class": "published-date"}
            )
            if date_elem:
                metadata["published_date"] = date_elem.get_text().strip()

            # Guideline code (e.g., NG28)
            code_match = re.search(r"\(([A-Z]{2,3}\d+)\)", title)
            if code_match:
                metadata["guideline_code"] = code_match.group(1)

            # Extract main content sections
            content_sections = []

            # Find main content div - NICE uses specific structure
            main_content = (
                soup.find("div", {"class": "content"})
                or soup.find("main")
                or soup.find("article")
            )

            if main_content:
                # Extract all headings and their content
                all_headings = main_content.find_all(["h1", "h2", "h3", "h4", "h5"])

                for heading in all_headings:
                    heading_text = heading.get_text().strip()

                    # Find content between this heading and the next
                    content_parts = []
                    current = heading.find_next_sibling()

                    while current and current.name not in [
                        "h1",
                        "h2",
                        "h3",
                        "h4",
                        "h5",
                    ]:
                        if current.name == "p":
                            text = current.get_text().strip()
                            if text:
                                content_parts.append(text)
                        elif current.name in ["ul", "ol"]:
                            items = current.find_all("li")
                            for li in items:
                                content_parts.append(f"  • {li.get_text().strip()}")
                        elif current.name == "div":
                            # Check if div has paragraphs
                            paras = current.find_all("p", recursive=False)
                            for p in paras:
                                text = p.get_text().strip()
                                if text:
                                    content_parts.append(text)

                        current = current.find_next_sibling()

                    if content_parts:
                        content_sections.append(
                            {
                                "heading": heading_text,
                                "content": "\n\n".join(content_parts),
                            }
                        )

                # If no sections found with headings, extract all paragraphs
                if not content_sections:
                    all_paragraphs = main_content.find_all("p")
                    all_text = "\n\n".join(
                        [
                            p.get_text().strip()
                            for p in all_paragraphs
                            if p.get_text().strip()
                        ]
                    )
                    if all_text:
                        content_sections.append(
                            {"heading": "Content", "content": all_text}
                        )

            # Compile full text
            full_text_parts = []
            for section in content_sections:
                if section["heading"]:
                    full_text_parts.append(f"## {section['heading']}")
                full_text_parts.append(section["content"])

            full_text = "\n\n".join(full_text_parts)

            # Extract recommendations specifically
            recommendations = []
            rec_sections = soup.find_all(
                ["div", "section"], class_=re.compile(r"recommendation")
            )
            for rec in rec_sections[:20]:  # Limit to first 20 recommendations
                rec_text = rec.get_text().strip()
                if rec_text and len(rec_text) > 20:
                    recommendations.append(rec_text)

            return {
                "url": url,
                "title": title,
                "metadata": metadata,
                "full_text": full_text,
                "full_text_length": len(full_text),
                "sections_count": len(content_sections),
                "recommendations": recommendations[:20] if recommendations else None,
                "recommendations_count": len(recommendations) if recommendations else 0,
                "source": "NICE",
                "content_type": "full_guideline",
                "success": len(full_text) > 500,
            }

        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to fetch NICE guideline: {str(e)}", "url": url}
        except Exception as e:
            return {"error": f"Error parsing NICE guideline: {str(e)}", "url": url}


@register_tool()
class WHOGuidelineFullTextTool(BaseTool):
    """
    Fetch full text content from WHO guideline pages.
    Takes a WHO publication URL and extracts content or PDF download link.
    """

    def __init__(self, tool_config):
        super().__init__(tool_config)
        self.base_url = "https://www.who.int"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def run(self, arguments):
        url = arguments.get("url", "")

        if not url:
            return {"error": "URL parameter is required"}

        # Ensure it's a WHO URL
        if "who.int" not in url:
            return {"error": "URL must be a WHO publication URL (who.int)"}

        return self._fetch_who_guideline(url)

    def _fetch_who_guideline(self, url):
        """Fetch WHO guideline content and PDF link."""
        try:
            time.sleep(1)  # Be respectful
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract title
            title_elem = soup.find("h1") or soup.find("title")
            title = title_elem.get_text().strip() if title_elem else "Unknown Title"

            # Extract metadata
            metadata = {}

            # Publication date
            date_elem = soup.find("time") or soup.find(
                "span", class_=re.compile(r"date")
            )
            if date_elem:
                metadata["published_date"] = date_elem.get_text().strip()

            # ISBN
            isbn_elem = soup.find(text=re.compile(r"ISBN"))
            if isbn_elem:
                isbn_match = re.search(r"ISBN[:\s]*([\d\-]+)", isbn_elem)
                if isbn_match:
                    metadata["isbn"] = isbn_match.group(1)

            # Find PDF download link
            pdf_link = None
            pdf_links = soup.find_all("a", href=re.compile(r"\.pdf$", re.I))

            for link in pdf_links:
                href = link.get("href", "")
                if href:
                    # Make absolute URL
                    if href.startswith("http"):
                        pdf_link = href
                    elif href.startswith("//"):
                        pdf_link = "https:" + href
                    elif href.startswith("/"):
                        pdf_link = self.base_url + href
                    else:
                        pdf_link = self.base_url + "/" + href

                    # Prefer full document over excerpts
                    link_text = link.get_text().lower()
                    if "full" in link_text or "complete" in link_text:
                        break

            # Extract overview/description
            overview = ""
            overview_section = soup.find(
                "div", class_=re.compile(r"overview|description|summary")
            ) or soup.find(
                "section", class_=re.compile(r"overview|description|summary")
            )

            if overview_section:
                paragraphs = overview_section.find_all("p")
                overview = "\n\n".join(
                    [p.get_text().strip() for p in paragraphs if p.get_text().strip()]
                )

            # Extract key facts/highlights
            key_facts = []
            facts_section = soup.find(
                ["div", "section"], class_=re.compile(r"key.*facts|highlights")
            )
            if facts_section:
                items = facts_section.find_all("li")
                key_facts = [
                    li.get_text().strip() for li in items if li.get_text().strip()
                ]

            # Try to extract main content
            main_content = ""
            content_div = (
                soup.find("div", {"class": "content"})
                or soup.find("main")
                or soup.find("article")
            )

            if content_div:
                # Get all paragraphs
                paragraphs = content_div.find_all("p")
                content_parts = []
                for p in paragraphs[:50]:  # Limit to avoid too much content
                    text = p.get_text().strip()
                    if len(text) > 30:  # Skip very short paragraphs
                        content_parts.append(text)

                main_content = "\n\n".join(content_parts)

            return {
                "url": url,
                "title": title,
                "metadata": metadata,
                "overview": overview,
                "main_content": main_content,
                "content_length": len(main_content),
                "key_facts": key_facts if key_facts else None,
                "pdf_download_url": pdf_link,
                "has_pdf": pdf_link is not None,
                "source": "WHO",
                "content_type": "guideline_page",
                "success": len(overview) > 100 or pdf_link is not None,
                "note": (
                    "Full text available as PDF download"
                    if pdf_link
                    else "Limited web content available"
                ),
            }

        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to fetch WHO guideline: {str(e)}", "url": url}
        except Exception as e:
            return {"error": f"Error parsing WHO guideline: {str(e)}", "url": url}
