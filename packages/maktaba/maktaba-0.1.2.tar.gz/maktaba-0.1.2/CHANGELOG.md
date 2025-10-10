# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2025-10-10

### Added
- ZeroEntropy Zerank reranker support via `ZerankReranker` class
- New optional dependency group: `zeroentropy`
- Async reranking with graceful fallback to heuristic scoring
- Comprehensive test coverage for Zerank reranker

## [0.1.0] - 2025-10-09

### Added
- Query pipeline with automatic reranking and citation formatting
- Ingestion pipeline for document processing
- Provider-agnostic embedding support (OpenAI, Azure, Cohere, Voyage)
- Vector store integrations (Qdrant, Pinecone, Chroma, Redis)
- Unstructured document chunking via LlamaIndex
- Cohere reranking support
- Async-first API design
- Full type hints and Pydantic validation
- Comprehensive test coverage
- Arabic and multilingual language support

### Documentation
- Overview, quickstart, and provider guides
- Example scripts for common use cases
- API reference documentation

[Unreleased]: https://github.com/nuhatech/maktaba/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/nuhatech/maktaba/compare/v0.1.0...v0.1.2
[0.1.0]: https://github.com/nuhatech/maktaba/releases/tag/v0.1.0
