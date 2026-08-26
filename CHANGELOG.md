# Changelog

Each milestone was committed and pushed to GitHub separately.

## [1.0.0]

- **M0** — project skeleton: configuration, provider abstractions, FastAPI health check, CI.
- **M1** — document ingestion: PDF/Word/Markdown → chunk → embed → SQLite, cited Q&A via CLI/API.
- **M2** — web portal: JWT login, document upload/management, chat with citations.
- **M3** — code + schematic ingestion: structure-aware code splitting, VLM description of schematics.
- **M4** — retrieval quality: hybrid BM25+vector (RRF), pluggable rerank, Hit@k/MRR evaluation.
- **M5** — dual portal & access control: RBAC roles + customer/model collection ACL.
- **M6** — Q&A loop: logging, feedback, similar questions, FAQ promotion.
- **M7** — engineering: Docker image + compose, request logging, store backup, v1.0.0 release.
