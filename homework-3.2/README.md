# Homework 3.2 — Alarm verification (Isolation Forest + AWS)

Python pipeline that trains an **Isolation Forest** on alarm **CSV** data, exports `**model/isolation_forest.joblib`**, and exposes `**POST /verify`** on **AWS** via **Lambda**, **API Gateway (HTTP API)**, and **S3** for model storage. Heavy dependencies run in a **Lambda layer** (numpy, scipy, scikit-learn, joblib) built with **AWS SAM**

## What is implemented


| Area           | Implementation                                                                                       |
| -------------- | ---------------------------------------------------------------------------------------------------- |
| Data           | `data/alarms.csv` (synthetic alarms); optional regeneration via `scripts/generate_alarms_csv.py`     |
| Training       | `train.py` — `sklearn.ensemble.IsolationForest`, writes `model/*.joblib` + `feature_columns.json`    |
| Inference      | `lambda/app.py` — loads model + metadata from **S3** into `/tmp`, parses JSON body, returns scores   |
| Infrastructure | `template.yaml` — **S3** bucket, **Lambda layer**, **Lambda** function, **HTTP API** `POST /verify`  |
| Local parity   | `sam build --use-container`; optional `**sam local start-api`** against real S3 using `**env.json`** |


Default stack behaviour: **Python 3.12**, Lambda **x86_64**, example region `us-east-1` (change in deploy config if you use another region)

## Prerequisites


| Requirement        | Notes                                                                                               |
| ------------------ | --------------------------------------------------------------------------------------------------- |
| **Python 3.12+**   | For the local training virtualenv (Lambda uses 3.12).                                               |
| **Docker Desktop** | Running, for `sam build --use-container` and `sam local …`.                                         |
| **AWS CLI**        | Configured (`aws configure`); prefer an **IAM user** with deploy permissions over root access keys. |
| **AWS SAM CLI**    | `sam --version`.                                                                                    |
| **AWS account**    | Ability to create CloudFormation stacks, Lambda, API Gateway, and S3.                               |


**Paths with spaces:** If the repo path contains spaces or `&`, quote it in the shell, for example:

```bash
cd "/path/to/hw3-security-cloud-ai/homework-3.2"
```

## Train the model (local)

```bash
cd homework-3.2
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-train.txt
```

Optional: regenerate CSV, then train:

```bash
python scripts/generate_alarms_csv.py   # writes data/alarms.csv
python train.py                         # writes model/isolation_forest.joblib and model/feature_columns.json
```

Check artifacts:

```bash
ls -la model/
```

## Build and deploy (SAM)

From `homework-3.2/`:

```bash
sam validate --region us-east-1 -t template.yaml
sam build --use-container
sam deploy --guided
```

On first `**sam deploy --guided**`, typical choices:

- Stack name and region: your choice (e.g. stack name `homework-32-verify`, region `us-east-1`)
- **Allow SAM CLI IAM role creation:** `yes`
- **Disable rollback:** `no` (or accept default) so failed deploys roll back cleanly
- `**VerifyFunction` has no authentication. Is this okay?** `**yes`** — the HTTP API has **no** API-key / JWT authorizer (public `POST /verify`). Answering **no** stops deploy with *Security Constraints Not Satisfied*
- **Save arguments to `samconfig.toml`:** `yes` for faster later deploys

The IAM principal used by the CLI needs permissions to create/update CloudFormation stacks and related resources. For a personal sandbox account, attaching `AdministratorAccess` to that IAM user is the simplest unblock; reduce scope for real production accounts.

After a successful deploy, read **CloudFormation → your stack → Outputs**:

- `HttpApiUrl` — base URL for the HTTP API
- `ModelBucketName` — S3 bucket where the model files must be uploaded

Subsequent deploys (when `samconfig.toml` exists):

```bash
sam deploy
```

## Upload model files to S3

The function reads `**models/isolation_forest.joblib**` and `**models/feature_columns.json**` from the stack bucket (keys must match `MODEL_KEY` / `META_KEY` in `template.yaml`)

```bash
BUCKET=<ModelBucketName-from-CloudFormation-Outputs>
aws s3 cp model/isolation_forest.joblib s3://$BUCKET/models/isolation_forest.joblib
aws s3 cp model/feature_columns.json s3://$BUCKET/models/feature_columns.json
aws s3 ls s3://$BUCKET/models/
```

Until both objects exist, inference calls may fail with S3 “not found” style errors in the JSON error payload

## API quick reference

**Base URL:** the `HttpApiUrl` value from stack outputs (no trailing slash required).  
**Endpoint:** `**POST {HttpApiUrl}/verify`**

Header:

```http
Content-Type: application/json
```

Example body (field names must match `feature_columns.json` produced by training):

```json
{
  "duration_sec": 15.5,
  "peak_amplitude": 0.22,
  "repetition_count": 35,
  "hour_of_day": 3
}
```

### Example with `curl`

Replace `YOUR_HTTP_API_URL` with the full `HttpApiUrl` value (it already points at the HTTP API host; append `**/verify**`).

```bash
curl -s -X POST "YOUR_HTTP_API_URL/verify" \
  -H "Content-Type: application/json" \
  -d '{"duration_sec":15.5,"peak_amplitude":0.22,"repetition_count":35,"hour_of_day":3}'
```

**Successful response (shape):** JSON including `**likely_false_alarm`** (boolean), `**isolation_forest_prediction`** (`1` = inlier, `-1` = outlier), `**anomaly_score**`, and `**interpretation**`. The first call after idle can take several seconds (cold start, S3 download, libraries)

## SAM local (optional)

Runs the Lambda in Docker on **[http://127.0.0.1:3000/verify](http://127.0.0.1:3000/verify)** but still uses **real S3** with your AWS credentials. SAM may not inject the same `MODEL_BUCKET` resolution as in the cloud, so provide `**env.json`**:

1. Copy `**env.json.example`** to `**env.json**`
2. Set `**MODEL_BUCKET**` to your stack’s `ModelBucketName` output
3. `**env.json**` is listed in `.gitignore` — keep bucket names and account-specific values out of version control if you prefer

```bash
sam build --use-container
sam local start-api --env-vars env.json
```

Send **POST** requests only (e.g. Postman or `curl`); opening `/verify` in a browser issues **GET**, which does not match the route

One-shot invoke:

```bash
sam local invoke VerifyFunction -e events/verify-post.json --env-vars env.json
```

## Configuration (`template.yaml` and runtime)


| Item                         | Purpose                                                                                               |
| ---------------------------- | ----------------------------------------------------------------------------------------------------- |
| `Globals.Function`           | `Runtime: python3.12`, `Architectures: [x86_64]`, `Timeout`, `MemorySize`                             |
| `VerifyFunction` environment | `MODEL_BUCKET`, `MODEL_KEY`, `META_KEY` — set by SAM from the template (bucket reference + key paths) |
| `SklearnLayer`               | Built from `layers/sklearn/` with `Metadata: BuildMethod: python3.12`                                 |
| `S3ReadPolicy`               | Lets the function read only the stack’s model bucket                                                  |


For production hardening you would add authentication on the HTTP API, tighten IAM, and use private buckets / VPC as needed

## Project layout

```
homework-3.2/
├── README.md
├── template.yaml
├── samconfig.toml.example
├── requirements-train.txt
├── train.py
├── env.json.example
├── events/
│   └── verify-post.json
├── lambda/
│   ├── app.py
│   └── requirements.txt
├── layers/
│   └── sklearn/
│       └── requirements.txt
├── scripts/
│   ├── generate_alarms_csv.py
│   └── AI_PROMPT_FOR_ALARMS.md
├── data/
│   └── alarms.csv
├── model/                         # produced by train.py (artifacts not always committed)
│   ├── isolation_forest.joblib
│   └── feature_columns.json
└── docs/                          # extra write-ups / images (optional)
```

## Typical HTTP behaviour (`POST /verify`)


| Code    | Typical cause                                                                          |
| ------- | -------------------------------------------------------------------------------------- |
| **200** | Valid JSON body; model present in S3; inference succeeded                              |
| **400** | Malformed JSON, missing feature keys, or non-numeric feature values                    |
| **500** | Misconfigured `MODEL_BUCKET`, missing S3 objects, or runtime errors inside the handler |


The API Gateway route itself is **POST-only**; **GET** `/verify` (e.g. from a browser tab) does not match the integration

## Troubleshooting (short)


| Symptom                                            | What to try                                                                                               |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `sam build --use-container` — no container runtime | Start Docker Desktop; confirm `docker ps` works                                                           |
| Deploy — *Security Constraints Not Satisfied*      | Answer `yes` to the “no authentication” prompt for this template                                          |
| Deploy — `AccessDenied` on CloudFormation          | Grant the CLI IAM user broader permissions (e.g. `AdministratorAccess` on a dev account)                  |
| Response JSON mentions **HeadObject / Not Found**  | Upload both model files under `models/` on the **same** bucket as `MODEL_BUCKET`; verify with `aws s3 ls` |
| `sam local` S3 errors but cloud works              | Use `**--env-vars env.json`** with the correct `MODEL_BUCKET`; confirm AWS credentials on the host        |
| Local or first request very slow                   | Cold start + **x86_64** emulation on Apple Silicon; retry or rely on the deployed API                     |


## Tech stack

- **Python 3.12** (Lambda runtime; local training venv should match closely)
- **scikit-learn**, **pandas**, **joblib** (training); **boto3** in the Lambda package for S3
- **AWS SAM** / **CloudFormation** — S3, Lambda, Lambda layer, HTTP API (API Gateway v2)
- **Docker** — reproducible Linux builds for Lambda and `sam local`

