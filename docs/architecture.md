# Architecture Decision Record

## Context

The application has one small web client, one HTTP API, seven fixed source pages, and one RAG workflow. It must be easy to explain and modify during a 45-minute review call.

## Decision

Use a modular monolith with Clean/Hexagonal boundaries.

- React/TypeScript owns browser interaction only.
- FastAPI owns transport and runtime composition.
- Application use cases own workflow decisions.
- Domain code owns framework-free entities, value objects, and safety policies.
- Infrastructure adapters own external providers, HTTP crawling, storage, and retrieval algorithms.

## Dependency rule

Inner layers never import outer layers. The application layer refers to external behavior through small `Protocol` ports. `ApplicationContainer` is the only composition root that selects concrete implementations.

## Extension examples

- Replace BM25: implement `RetrieverPort` and change one container binding.
- Add Claude: implement `LLMPort` and change one container binding.
- Add PostgreSQL: implement `KnowledgeRepository` and `GapRepository`.
- Add a safety rule: append a policy to `SafetyPolicyChain`.
- Replace React: preserve the `/api` schemas; backend business code is unaffected.

## Consequences

The repository contains more small files than the original prototype, but each has a narrow reason to change. A separate AI microservice was rejected because it would introduce a network boundary, independent deployment, authentication, and distributed failure modes without a reuse or scaling requirement.

