## 1. Executive Summary

This document presents a comprehensive, production-ready plan to build an **anomaly detection system** for financial transactions in a banking environment where:

- The transaction database is very large (scales to millions or billions of rows).
    
- There are **no ground-truth fraud labels** available initially.
    

Goals: model normal behavior at scale, detect deviations as candidate frauds, provide a robust human-in-the-loop feedback pipeline to produce labeled data over time, and evolve into a hybrid unsupervised + supervised production system.

---

## 2. Project Objectives and Scope

### Objectives

- Detect anomalous transactions with high recall while maintaining analyst workload within operational constraints.
    
- Make anomaly scoring low-latency for real-time decisioning and high-throughput for batch analysis.
    
- Provide an auditable pipeline and explainable signals to fraud analysts and compliance.
    
- Create a feedback loop to collect labeled fraud cases for future supervised learning.
    

### Scope (in-scope)

- Transaction-level feature engineering and account-level aggregates.
    
- Unsupervised anomaly detection methods (Isolation Forest, Autoencoders, clustering).
    
- Streaming and batch scoring pipelines.
    
- Analyst dashboard + case management integration.
    
- Model monitoring, drift detection, and retraining processes.
    

### Out of scope (for initial phase)

- Full replacement of rule-based systems (we will integrate with, not replace, existing rules).
    
- Investigation workflows and legal processes beyond flagging and case creation.
    

---

## 3. Assumptions & Constraints

- Raw transaction schema contains at minimum: transaction_id, account_id, timestamp, amount, merchant_id, merchant_category, channel (ATM/pos/online), geo (country/city/IP), device_id.
    
- No labeled frauds initially; analyst labeling will begin after model rollout.
    
- Infrastructure can provision cluster compute (Spark/Dask) and streaming (Kafka).
    
- Compliance team requires explainability and retention of scored results for audit.
    

---

## 4. Data Requirements & Preprocessing

### Required fields (minimum)

- `transaction_id`, `account_id`, `timestamp`, `amount`, `merchant_id`, `merchant_category`, `channel`, `country`, `device_id`, `currency`.
    

### Optional / beneficial fields

- `ip_address`, `card_id`, `card_present_flag`, `previous_balance`, `settlement_status`.
    

### Preprocessing steps

1. **Schema normalization** — canonicalize merchant categories, channels, and country codes.
    
2. **Data quality checks** — missing timestamps, negative amounts, duplicate transaction IDs.
    
3. **Currency normalization** — convert to base currency for modeling.
    
4. **Feature aggregations** — rolling windows (1h, 24h, 7d, 30d) per account: counts, sums, unique merchants.
    
5. **Sessionization / Journeys** — group transactions by short time windows when appropriate (e.g., web session).
    
6. **Anonymization & privacy** — mask PII where required; preserve features necessary for detection while meeting privacy/compliance.
    

### Storage & feature store

- Store raw data in a data lake (Parquet on object store) and derived features in a feature store (Feast/Hopsworks or Spark table).
    
- Keep feature versions and model inputs for reproducibility.
    

---

## 5. Feature Engineering (detailed)

### Transaction-level features

- `amount` and normalized `amount_relative_to_account_mean` (z-score or percentile).
    
- `hour_of_day`, `day_of_week` (cyclical encoding).
    
- `merchant_category` embedding or one-hot.
    
- `channel` (ATM, POS, WEB, MOBILE).
    
- `is_international` flag, `country_distance_from_home` (haversine / geodistance where geo exists).
    

### Account-aggregate features (rolling windows)

- `txn_count_1h`, `txn_sum_1h`, `txn_count_24h`, `txn_sum_24h`, `txn_count_7d`, `txn_sum_7d`.
    
- `unique_merchants_7d`, `avg_amount_30d`, `std_amount_30d`.
    
- `ratio_international_30d`, `median_intertxn_time`.
    

### Behavioral & derived features

- `velocity_features` (transactions per minute/hour).
    
- `novel_merchant_flag` (merchant not seen for account in last N days).
    
- `device_change_flag` (first use of device_id or IP).
    
- `sudden_balance_change_flag` (if `previous_balance` available).
    

### Feature encodings & scaling

- Use robust scaling (median & IQR) to reduce influence of heavy tails.
    
- Embeddings for categorical features with many levels (merchant_id).
    

---

## 6. Modeling Strategy

Because labels are absent, start with **unsupervised and semi-supervised** approaches, progressing to hybrid models as labels accumulate.

### Baseline approaches (fast to prototype)

- **Statistical rules**: z-score on normalized amount and velocity heuristics for immediate baseline.
    
- **Isolation Forest**: scalable, interpretable anomaly score. Use Spark MLlib or distributed scikit-learn for prototyping.
    
- **Local Outlier Factor / DBSCAN** for clustering-based outlier detection (on sampled data).
    

### Advanced approaches

- **Deep Autoencoder (dense / sequence)** trained on majority of data assumed normal; anomalies = high reconstruction error.
    
- **Variational Autoencoder (VAE)** for probabilistic scoring.
    
- **Sequence models** (LSTM / Transformer) on transaction sequences per account to detect anomalous sequences.
    
- **Graph-based anomaly detection** leveraging merchant-customer graphs (detect suspicious bipartite structures).
    

### Practical notes on training

- Train on a representative sample of data considered "normal" (exclude the extreme top X% of scores iteratively).
    
- Use feature drift monitoring and re-sampling strategies to adapt to seasonal behavior.
    

---

## 7. Evaluation Strategy (no labels)

Evaluation without labels is fundamentally different. Adopt a mixed quantitative + qualitative approach:

### Quantitative proxies & metrics

- **Score distribution stability** (monitor percentiles over time).
    
- **Precision@k** via manual labeling: sample top k anomalies weekly and measure how many are true frauds after analyst review.
    
- **Time-to-detection** for known historical incidents (if historical fraud incident timestamps exist).
    
- **Alert volume** (alerts/day) vs. analyst capacity (target false positive budget).
    

### Human-in-the-loop validation

- Regular sampling of flagged and non-flagged transactions for analyst review.
    
- Use analyst feedback to build a labeled dataset and compute standard metrics (precision, recall, F1) once labels exist.
    

### A/B and Canary testing

- Canary new models on a slice of traffic (e.g., 1% of transactions) and measure analyst feedback and downstream false-positive rates.
    

---

## 8. Deployment & Architecture

### High-level architecture (textual)

1. **Ingestion layer**: Kafka or Kinesis receives transaction events from core banking.
    
2. **Streaming processing**: Spark Structured Streaming / Flink consumes events, performs lightweight enrichment and feature lookups (from feature store).
    
3. **Feature store**: Online store holds last-N aggregates for low-latency scoring, offline store holds historical features.
    
4. **Model scoring**: Real-time scorer (Java/Scala or Python microservice) computes anomaly score and attaches explanation signals.
    
5. **Alerting & Case Management**: High-score transactions are forwarded to an alerts queue and the fraud case management system (e.g., NICE Actimize, SAS).
    
6. **Batch pipeline**: Nightly retraining using Spark on historical features; generate model artifacts in model registry.
    
7. **Monitoring & Feedback**: Metrics, model drift detectors, and human feedback ingestion channel to the labeled dataset store.
    

### Non-functional requirements

- **Latency**: <100 ms for real-time decisioning (if operational); otherwise define acceptable SLA (e.g., <1s).
    
- **Throughput**: Support peak TPS with headroom (specify expected TPS).
    
- **Scalability**: Horizontal scaling for both streaming and batch.
    
- **Auditability**: Persist scored outputs and model versions for at least retention_period (spec compliance).
    

---

## 9. Monitoring, Explainability & Compliance

### Monitoring

- Data quality (missing fields, schema changes), feature drift (statistical shift), model performance proxies (score percentiles), alert volumes, latency, and system health.
    

### Explainability

- Provide per-transaction signal contributions (feature importance, reconstruction error components, nearest-normal examples).
    
- For tree-based models use SHAP / feature contributions; for autoencoders provide top contributing features to reconstruction error.
    

### Compliance & Audit

- Log model version, feature snapshot, input transaction, and scored output for every decision that resulted in a case.
    
- Ensure retention and data masking according to bank policy and GDPR/local regulations.
    

---

## 10. Human-in-the-loop & Labeling Strategy

- **Analyst review UI**: present flagged transactions with explanations and helper signals.
    
- **Label capture**: labels: `confirmed_fraud`, `false_positive`, `suspicious_unconfirmed`.
    
- **Label storage**: store labeled examples in a secure dataset linked to model artifact IDs and features.
    
- **Active learning**: prioritize uncertain examples and high-impact cases for labeling to maximize information gain.
    

---

## 11. Operational Processes

- **Model retraining cadence**: baseline weekly for heavy drift environments; monthly otherwise.
    
- **Canary & rollout**: phased 1% → 5% → 25% → 100% with rollback plan.
    
- **Incident response**: SLA for false-positive spikes, data drift alerts, and model rollback.
    

---

## 12. Roles & Responsibilities

- **Product Manager (Fraud Product Owner)** — defines detection objectives, analyst capacity, KPIs, and compliance needs.
    
- **Data Engineer** — ingestion pipelines, feature pipelines, feature store, data quality, and ETL (Spark/Kafka).
    
- **Data Scientist / ML Engineer** — model selection, training, evaluation, and experiment tracking (MLflow).
    
- **MLops / DevOps Engineer** — deployment automation, model registry, CI/CD, monitoring, and infra.
    
- **Fraud Analyst / SME** — validates flagged transactions, provides labels and rules, and tunes thresholds.
    
- **Compliance Officer / Legal** — ensures policy, auditability, and data privacy are honored.
    
- **QA / Testing** — ensures pipeline correctness, regression testing, and performance tests.
    

---

## 13. Project Plan & Milestones (example timeline)

This is a suggested 16-week phased plan for an initial MVP.

- **Weeks 0–2 — Discovery & Data Exploration**
    
    - Confirm data availability and sample dataset extraction.
        
    - Define success metrics and analyst capacity.
        
- **Weeks 3–6 — Feature Engineering & Baseline Models**
    
    - Build feature pipelines and offline feature store.
        
    - Implement statistical baselines and Isolation Forest prototype.
        
    - Deliver analyst UI mockups.
        
- **Weeks 7–10 — Streaming & Real-time Scoring (MVP)**
    
    - Implement streaming enrichment and real-time scoring microservice.
        
    - Integrate with alert queue/case management.
        
- **Weeks 11–14 — Human-in-the-loop & Labeling**
    
    - Launch analyst review workflow, capture labels.
        
    - Begin semi-supervised experiments and active learning.
        
- **Weeks 15–16 — Harden, Monitor & Rollout**
    
    - Add monitoring, drift detection, and canary rollout.
        
    - Finalize SOPs and handover to operations.
        

Deliverables: data spec, feature store, model artifacts, scoring service, analyst dashboard, SOPs, and monitoring dashboards.

---

## 14. Technology & Tools Recommendation

- **Data ingestion & streaming**: Kafka / Kinesis
    
- **Batch & stream processing**: Apache Spark (Structured Streaming) or Flink
    
- **Feature store**: Feast or managed alternative
    
- **Modeling / Experimentation**: Python (scikit-learn, PyTorch/TensorFlow), MLflow for tracking
    
- **Serving**: Model server (BentoML, KFServing) or lightweight microservice in Go/Java/Python
    
- **Storage**: Object store (S3-compatible), Parquet files, Columnar DB for OLAP (ClickHouse or Redshift/Snowflake)
    
- **Monitoring**: Prometheus + Grafana, plus custom dashboards for score distribution
    
- **Case management**: Integrate with existing system (NICE, SAS, or internal CRM)
    

---

## 15. Risks & Mitigations

- **High false-positive rate** → pilot conservative thresholds; use two-stage gating (anomaly score + tighter rule).
    
- **Data drift** → automated drift detectors + scheduled retrain.
    
- **Scale & cost** → prototype with sampled data + right-size compute; use spot/preemptible instances where possible.
    
- **Lack of labeled data** → accelerate labeling via active learning and analyst-in-the-loop workflows.
    

---

## 16. Example SQL & Pseudocode

### Rolling feature (example SQL for Spark / Hive)

```
-- 24-hour txn count per account
SELECT
  account_id,
  window_start,
  COUNT(*) as txn_count_24h,
  SUM(amount) as txn_sum_24h
FROM transactions
GROUP BY account_id, window(window_timestamp, '24 hours')
```

### Pseudocode: simple scoring flow

```
# Load model and feature store
features = feature_store.lookup(account_id, last_n_days)
scores = model.score(features)
if scores['anomaly_score'] > threshold:
    send_alert(transaction_id, scores, explanation)
```

---

## 17. Success Criteria

- **Operational**: Real-time scoring latency meets SLA; alert volume within analyst capacity.
    
- **Detection**: Precision@k (k = top weekly alerts) meets business-defined minimum after initial labeling period.
    
- **Process**: Labeled dataset grows to statistically useful size (e.g., >1k confirmed frauds) within N months.
    

---

## 18. Next Steps (immediate)

1. Extract a representative sample (1–10M rows) for prototyping and share with data engineering.
    
2. Confirm analyst capacity (alerts/day) and label retention policy with product and compliance.
    
3. Provision development cluster (Spark + Kafka) and a feature store sandbox.
    
4. Kick off Weeks 0–2 discovery tasks.
    

---

## Appendix A — Sample Features Checklist

- transaction_id
    
- account_id
    
- timestamp
    
- amount (normalized)
    
- channel
    
- merchant_category
    
- txn_count_1h / 24h / 7d
    
- unique_merchants_7d
    
- device_change_flag
    
- is_international
    

---

## Appendix B — Glossary

- **Anomaly score**: numeric score indicating how unusual a transaction is relative to a learned normal model.
    
- **Feature store**: centralized repository for serving features to both training and serving environments.
    
- **Reconstruction error**: for autoencoders, the difference between input and reconstructed output used as anomaly indication.
    

_This canvas is intended as a living document: iterate feature lists, thresholds, and timelines after initial discovery and the first analyst feedback loop._