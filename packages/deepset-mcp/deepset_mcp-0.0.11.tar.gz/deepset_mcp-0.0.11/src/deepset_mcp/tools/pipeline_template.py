# SPDX-FileCopyrightText: 2025-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

import numpy as np
from pydantic import BaseModel

from deepset_mcp.api.exceptions import ResourceNotFoundError, UnexpectedAPIError
from deepset_mcp.api.pipeline_template.models import (
    PipelineTemplate,
    PipelineType,
)
from deepset_mcp.api.protocols import AsyncClientProtocol
from deepset_mcp.api.shared_models import PaginatedResponse
from deepset_mcp.tools.model_protocol import ModelProtocol


async def list_templates(
    *,
    client: AsyncClientProtocol,
    workspace: str,
    limit: int = 100,
    pipeline_type: PipelineType | str | None = None,
    # after: str | None = None TODO
) -> PaginatedResponse[PipelineTemplate] | str:
    """Retrieves a list of all available pipeline and indexing templates.

    :param client: The async client for API requests.
    :param workspace: The workspace to list templates from.
    :param limit: Maximum number of templates to return (default: 100).
    :param pipeline_type: The type of pipeline to return.

    :returns: List of pipeline templates or error message.
    """
    try:
        return await client.pipeline_templates(workspace=workspace).list(
            limit=limit,
            filter=f"pipeline_type eq '{pipeline_type}'" if pipeline_type else None,  # TODO: after=after
        )
    except ResourceNotFoundError:
        return f"There is no workspace named '{workspace}'. Did you mean to configure it?"
    except UnexpectedAPIError as e:
        return f"Failed to list pipeline templates: {e}"


async def get_template(*, client: AsyncClientProtocol, workspace: str, template_name: str) -> PipelineTemplate | str:
    """Fetches detailed information for a specific pipeline or indexing template, identified by its `template_name`.

    :param client: The async client for API requests.
    :param workspace: The workspace to fetch template from.
    :param template_name: The name of the template to fetch.

    :returns: Pipeline or indexing template details or error message.
    """
    try:
        return await client.pipeline_templates(workspace=workspace).get_template(template_name=template_name)
    except ResourceNotFoundError:
        return f"There is no pipeline template named '{template_name}' in workspace '{workspace}'."
    except UnexpectedAPIError as e:
        return f"Failed to fetch pipeline template '{template_name}': {e}"


class PipelineTemplateSearchResult(BaseModel):
    """Model representing a search result for pipeline templates."""

    template: PipelineTemplate
    "Pipeline template that matched the search criteria"
    similarity_score: float
    "Relevance score indicating how well the template matches the search"


class PipelineTemplateSearchResults(BaseModel):
    """Response model for pipeline template search results."""

    results: list[PipelineTemplateSearchResult]
    "List of pipeline templates matching the search criteria"
    query: str
    "Original search query string"
    total_found: int
    "Total number of templates found matching the search criteria"


async def search_templates(
    *,
    client: AsyncClientProtocol,
    query: str,
    model: ModelProtocol,
    workspace: str,
    top_k: int = 10,
    pipeline_type: PipelineType | str = PipelineType.QUERY,
) -> PipelineTemplateSearchResults | str:
    """Searches for pipeline or indexing templates based on name or description using semantic similarity.

    :param client: The API client to use.
    :param query: The search query.
    :param model: The model to use for computing embeddings.
    :param workspace: The workspace to search templates from.
    :param top_k: Maximum number of results to return (default: 10).
    :param pipeline_type: The type of pipeline to return ('indexing' or 'query'; default: 'query').

    :returns: Search results with similarity scores or error message.
    """
    try:
        response = await client.pipeline_templates(workspace=workspace).list()
        templates = response.data

        # Filter by pipeline_type if specified
        if pipeline_type:
            templates = [t for t in templates if t.pipeline_type == pipeline_type]
    except UnexpectedAPIError as e:
        return f"Failed to retrieve pipeline templates: {e}"

    if not templates:
        return PipelineTemplateSearchResults(results=[], query=query, total_found=0)

    # Extract text for embedding from all templates
    template_texts: list[tuple[str, str]] = [
        (template.template_name, f"{template.template_name} {template.description}") for template in templates
    ]
    template_names: list[str] = [t[0] for t in template_texts]

    # Compute embeddings
    query_embedding = model.encode(query)
    template_embeddings = model.encode([text for _, text in template_texts])

    query_embedding_reshaped = query_embedding.reshape(1, -1)

    # Calculate dot product between target and all templates
    # This gives us a similarity score for each template
    similarities = np.dot(template_embeddings, query_embedding_reshaped.T).flatten()

    # Create (template_name, similarity) pairs
    template_similarities = list(zip(template_names, similarities, strict=False))

    # Sort by similarity score in descending order
    template_similarities.sort(key=lambda x: x[1], reverse=True)

    top_templates = template_similarities[:top_k]
    search_results = []
    for template_name, sim in top_templates:
        # Find the template object by name
        template = next((t for t in templates if t.template_name == template_name), None)
        if template:
            search_results.append(PipelineTemplateSearchResult(template=template, similarity_score=float(sim)))

    return PipelineTemplateSearchResults(results=search_results, query=query, total_found=len(search_results))
