# WatchTower


WatchTower is a project-aware FastAPI runtime observability tool that maps requests to user-defined classes and functions, helping developers understand request flow and inspect profiling data without framework noise.


### Best MVP plan now

#### Task 1

Build indexer.py

#### Task 2

Generate code_index.json

#### Task 3

Make middleware load this index at startup

#### Task 4

When request trace is saved, filter raw trace to indexed code only

#### Task 5

Build request tree from filtered events

#### Task 6

Render sunburst