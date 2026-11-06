"""Bulk mode (specs/bulk-mode.md, owner decision 2026-11-06): research once (dossier), write many (Message Batches API).

Stages: crawl → extract (batch) → dossier → questions → rank → plan → gather → write (batch) → check → verify (batch) → publish.
Only extract, write and verify call a model; everything else is code. `python -m campus_worker.bulk --help` lists the commands.
"""
