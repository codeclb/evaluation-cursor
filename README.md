# Cursor Evaluation

This repository is used to evaluate Cursor-assisted implementation quality across multiple attempts of the same TXT word frequency analyzer problem.

## Evaluation Focus

- Delivering the same product outcome (TXT upload + word frequency lookup) across different implementation passes
- Measuring iteration quality from simpler builds to more production-oriented architecture
- Comparing reliability, data persistence, API design, and frontend usability between attempts

## What Is In This Repo

- `AutoApp/attemptX/`  
  Attempts at creating app with Auto mode, using different levels of specificity and native Cursor tools 
- `PerformanceApp/attemptX/`  
  Attempts at creating app with Perfomance mode
- `EvaluationDemo/`  
  Evaluation support material (deck + glossary)

## Core Capabilities Being Compared

- Upload `.txt` files from a web UI
- Persist raw text and transformed analysis
- Query word occurrence counts for uploaded files
- Handle repeat usage patterns (history, duplicate behavior, retrieval flow)

## How To Use This Workspace For Evaluation

1. Run one attempt at a time from its own directory.
2. Execute the same functional checks in each attempt.
3. Compare outcomes on:
   - correctness
   - maintainability
   - operational readiness (tests, env setup, deployment path)
