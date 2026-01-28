# Design YAML Collection

A collection of YAML templates for defining system design standards, specifically for cloud-native, IoT, and microservices architectures.
Designed to be used as "Input" for AI agents to generate design documents and implementation code.

## Catalog

| Collection | Description | Links |
| :--- | :--- | :--- |
| **ai-data-readiness** | AI Data Readiness Check. Quality criteria for AI-ready data formatting. | [README (JP)](collection/ai-data-readiness/README.ja.md) |
| **api-design** | Web API Design Standards. Error handling, idempotency, security policies. | [README (JP)](collection/api-design/README.ja.md) |
| **data-shape-design** | Data Shape Design. Strategy for choosing between wide vs long table formats. | [README (JP)](collection/data-shape-design/README.ja.md) |
| **db-layer-responsibility** | DB Layer Responsibility. Architecture based on "DB as a Transit Point". | [README (JP)](collection/db-layer-responsibility/README.ja.md) |
| **logger** | Structured Logging Standards. Design for searchability, monitoring, and PII protection. | [README (JP)](collection/logger/README.ja.md) |
| **messaging-design** | Async Messaging Design. Ordering guarantees, idempotency, DLQ strategies. | [README (JP)](collection/messaging-design/README.ja.md) |
| **ot-it-boundary-design** | OT/IT Boundary Design. Safe integration protocols between control systems and IT. | [README (JP)](collection/ot-it-boundary-design/README.ja.md) |
| **persistence-design** | Persistence Layer Design. Store selection, schema management, backup strategies. | [README (JP)](collection/persistence-design/README.ja.md) |
| **release-strategy** | Release Strategy. CI/CD pipelines, Blue/Green deployment, quality gates. | [README (JP)](collection/release-strategy/README.ja.md) |
| **resiliency-design** | Resiliency Design. Circuit Breaker, Retry, Bulkhead patterns. | [README (JP)](collection/resiliency-design/README.ja.md) |

## Usage
See `README.ja.md` in each directory for example prompts (currently in Japanese) to instruct AI agents.
