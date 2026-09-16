# 5. API Gateway

## What Is It? (Plain English)

API Gateway puts a proper, managed front door in front of a backend service — with a plain API key for access instead of requiring callers to have a Google Cloud identity. It's how you'd expose `digest-worker` to something that isn't part of your GCP project at all, like a mobile app or a third-party integration.

## Why It Matters for AI Engineers

Every other trigger in this module assumes the caller has a Google identity (a service account, your own `gcloud` login). That's completely wrong for a public-facing caller. API Gateway is the pattern for "let outsiders in, safely, without giving them GCP access."

## Key Concepts

| Term | Meaning |
|------|---------|
| **OpenAPI Spec** | A YAML file describing your API's paths and how they map to a backend — new artifact type for this course |
| **`x-google-backend`** | The extension telling API Gateway which real URL a path actually routes to |
| **API Config** | A specific, immutable deployment of your OpenAPI spec |
| **Gateway** | The live, running instance serving traffic according to an API Config |
| **API Key** | A plain key a caller passes as a query parameter — no Google identity required |

## How It Fits Together

```mermaid
flowchart LR
    A["External caller<br/>(mobile app, etc.)"] -->|"?key=API_KEY"| B["API Gateway"]
    B -->|"x-google-backend routes to"| C["digest-worker-http<br/>(same function from topic 4)"]
```

## Step-by-Step

**1. Look at the OpenAPI spec** (`code/15-event-driven-ai-applications/05_openapi_spec.yaml`) — it defines a `/trigger-digest` path, routed via `x-google-backend` to `digest-worker-http`'s URL, requiring an API key.

**2. Create the logical API and deploy a config from the spec:**
```bat
gcloud api-gateway apis create %API_ID%

gcloud api-gateway api-configs create %API_CONFIG_ID% ^
  --api=%API_ID% ^
  --openapi-spec=05_openapi_spec.yaml ^
  --backend-auth-service-account=%WORKER_SA_EMAIL%
```

**3. Deploy the gateway itself:**
```bat
gcloud api-gateway gateways create %GATEWAY_ID% ^
  --api=%API_ID% ^
  --api-config=%API_CONFIG_ID% ^
  --location=%REGION%
```

**4. Create an API key:**
```bat
gcloud services api-keys create --display-name="Digest API Key"
```
Copy the key value from the output (or `gcloud services api-keys list` + `gcloud services api-keys get-key-string KEY_ID`).

**5. Get the gateway's hostname and test it:**
```bat
gcloud api-gateway gateways describe %GATEWAY_ID% --location=%REGION% --format="value(defaultHostname)"

curl "https://GATEWAY_HOSTNAME/trigger-digest?key=YOUR_API_KEY"
```

No `gcloud auth print-identity-token` anywhere in this test — that's the entire point of this topic.

## Common Pitfalls

- Forgetting `--backend-auth-service-account` — without it, API Gateway has no identity to call the locked-down Cloud Function with, and every request fails.
- Testing without the `?key=` query parameter — the OpenAPI spec's `securityDefinitions` requires it; a request without one is rejected before it ever reaches the backend.
- Treating API Gateway and Cloud Tasks as solving the same problem — API Gateway is about *who's allowed to call in from outside*; Cloud Tasks is about *reliable delivery of calls you're making yourself*.

## Quick Recap

1. Why doesn't this topic's test use an identity token like every earlier one did?
2. What does `x-google-backend` do inside the OpenAPI spec?
3. What would break if `--backend-auth-service-account` were left out of the api-config creation?
