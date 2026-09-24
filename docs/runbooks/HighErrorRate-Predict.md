# Runbook: High Error Rate on /api/predict

**Means:** The FastAPI application is experiencing consecutive 5xx errors. This typically occurs when a payload bypasses physical boundaries and triggers a NaN float error in the physics equations, or the ML models in `ModelRegistry` failed to load/allocate during the `lifespan` event.

**First check:** Search the structured JSON logs in the server console for `level: "ERROR"`. Ensure you isolate logs using the `request_id` correlation ID. Check if `calculate_antenna_metrics` is throwing a `ValueError` for invalid patch sizes, or if `xgboost` is returning inference errors. 

**Escalate to:** #physics-engine-oncall if it's a boundary constraint issue, or #ml-platform-oncall if the models are crashing.
