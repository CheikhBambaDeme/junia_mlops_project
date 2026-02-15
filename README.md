# 🏠 Housing Price Predictor — MLOps Project

A complete **local MLOps pipeline** for housing price prediction, built with Docker, FastAPI, Django, MLflow, and GitHub Actions.

> **Junia ISEN — MLOps Course Project**

---

## 📋 Table of Contents

- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [1. Clone & Configure](#1-clone--configure)
  - [2. Download the Dataset](#2-download-the-dataset)
  - [3. Build & Run](#3-build--run)
  - [4. Train the Model](#4-train-the-model)
  - [5. Use the App](#5-use-the-app)
- [API Documentation](#api-documentation)
- [CI/CD Pipeline](#cicd-pipeline)
  - [GitHub Actions Workflow](#github-actions-workflow)
  - [Setting up a Self-Hosted Runner](#setting-up-a-self-hosted-runner)
- [MLflow — Experiment Tracking](#mlflow--experiment-tracking)
- [Data Validation](#data-validation)
- [Model Versioning](#model-versioning)
- [Environment Variables](#environment-variables)
- [4-Phase Implementation Plan](#4-phase-implementation-plan)
- [Team](#team)

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              GitHub Actions (Self-Hosted Runner)        │
│  Triggers: model code change or new data pushed         │
│  → Validates data → Trains model → Deploys locally      │
└─────────────────────────────────────────────────────────┘
                            │
              docker compose up --build
                            │
         ┌──────────────────┴──────────────────┐
         ▼                                     ▼
┌──────────────────────┐           ┌──────────────────────┐
│  Container 1         │◄──────────│  Container 2         │
│  Training & API      │  HTTP     │  Django Frontend     │
│  (FastAPI)           │  REST     │                      │
│                      │           │  - User input form   │
│  - /train endpoint   │           │  - Calls /predict    │
│  - /predict endpoint │           │  - Shows results     │
│  - /metrics endpoint │           │                      │
│  - Model loaded at   │           │  Port: 8080          │
│    startup           │           └──────────────────────┘
│  Port: 8000          │
└──────────┬───────────┘
           │
    ┌──────┴──────┐
    │ Shared Vols │
    │ ./data      │
    │ ./models    │
    │ ./mlruns    │
    │ ./logs      │
    └─────────────┘
```

---

## Tech Stack

| Component              | Technology                     |
|------------------------|--------------------------------|
| **ML Model**           | scikit-learn (RandomForest)    |
| **Training/Inference API** | FastAPI + Uvicorn          |
| **Frontend**           | Django 4.2                     |
| **Containerization**   | Docker & Docker Compose        |
| **Experiment Tracking**| MLflow                         |
| **Data Validation**    | Pandera                        |
| **Model Serialization**| Joblib                         |
| **CI/CD**              | GitHub Actions (self-hosted)   |
| **Environment Mgmt**   | python-dotenv                 |
| **Dataset**            | [Kaggle — House Pricing](https://www.kaggle.com/datasets/nmnbabbar/house-pricing) |

---

## Project Structure

```
junia_mlops_project/
├── .github/
│   └── workflows/
│       └── train-pipeline.yml       # CI/CD pipeline
├── data/
│   ├── raw/
│   │   └── house_prices.csv         # Kaggle dataset (gitignored)
│   └── processed/
├── models/
│   └── artifacts/                   # Saved .joblib models (gitignored)
├── training-service/                # Container 1
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── model.py                 # Model architecture & preprocessing
│   │   ├── train.py                 # Training script (explicit save/load)
│   │   ├── inference.py             # Inference script (explicit load)
│   │   └── validate_data.py         # Data validation with Pandera
│   └── api/
│       └── main.py                  # FastAPI app (model loaded at startup)
├── django-service/                  # Container 2
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── housing_app/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── predictor/
│       ├── forms.py                 # Input form
│       ├── views.py                 # Prediction view (calls API)
│       ├── urls.py
│       └── templates/
│           └── predictor/
│               └── predict.html     # UI template
├── mlruns/                          # MLflow experiment data
├── logs/                            # Application logs
├── docker-compose.yml
├── .env                             # Environment variables (gitignored)
├── .env.example                     # Template for .env
├── .gitignore
└── README.md
```

---

## Getting Started

### Prerequisites

- **Docker** & **Docker Compose** installed
- **Git** installed
- **Kaggle account** (for downloading the dataset)
- **Python 3.10+** (only needed if running outside Docker)

### 1. Clone & Configure

```bash
git clone https://github.com/CheikhBambaDeme/junia_mlops_project.git
cd junia_mlops_project

# Create your .env from the template
cp .env.example .env
```

### 2. Download the Dataset

Option A — Using Kaggle CLI:
```bash
pip install kaggle
# Place your kaggle.json in ~/.kaggle/
kaggle datasets download -d nmnbabbar/house-pricing -p data/raw --unzip
```

Option B — Manual download:
1. Go to https://www.kaggle.com/datasets/nmnbabbar/house-pricing
2. Download the CSV
3. Place it at `data/raw/house_prices.csv`

**Dataset columns:** `HouseID`, `Location`, `Bedrooms`, `Bathrooms`, `SquareFeet`, `Price`
- 1000 rows
- 4 locations: New York, Los Angeles, Chicago, Houston

### 3. Build & Run

```bash
docker compose up --build
```

This starts:
- **Training API** at [http://localhost:8000](http://localhost:8000) (Swagger docs at [/docs](http://localhost:8000/docs))
- **Django App** at [http://localhost:8080](http://localhost:8080)

### 4. Train the Model

On first launch, no model is loaded. Train it by calling:

```bash
curl -X POST http://localhost:8000/train
```

Or open [http://localhost:8000/docs](http://localhost:8000/docs) and use the **POST /train** endpoint.

The model is automatically reloaded after training — no restart needed.

### 5. Use the App

Open [http://localhost:8080](http://localhost:8080) in your browser:
1. Enter housing features (bedrooms, bathrooms, sqft, location)
2. Click **Predict Price**
3. See the estimated price

---

## API Documentation

The FastAPI service auto-generates interactive docs at [http://localhost:8000/docs](http://localhost:8000/docs).

| Endpoint        | Method | Description                                  |
|-----------------|--------|----------------------------------------------|
| `/health`       | GET    | Health check + model loaded status           |
| `/predict`      | POST   | Make a price prediction                      |
| `/train`        | POST   | Trigger model retraining                     |
| `/metrics`      | GET    | Get current model metrics (RMSE, MAE, R²)    |

### Prediction Request Example

```json
{
  "Bedrooms": 3,
  "Bathrooms": 2,
  "SquareFeet": 1800,
  "Location": "Chicago"
}
```

### Prediction Response Example

```json
{
  "prediction": 245000.50,
  "model_version": "20260215_143022",
  "features_used": ["Bedrooms", "Bathrooms", "SquareFeet", "Location_encoded"]
}
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

The pipeline is defined in `.github/workflows/train-pipeline.yml` and triggers when:

| Trigger                          | Description                          |
|----------------------------------|--------------------------------------|
| Push to `training-service/src/**`| Model architecture or training code changes |
| Push to `data/raw/**`            | New or updated dataset               |
| Manual dispatch                  | Manually triggered from GitHub UI    |

**Pipeline stages:**
1. **🔍 Validate Data** — Runs Pandera schema validation
2. **🏋️ Train Model** — Builds container, trains model, logs metrics
3. **🚀 Deploy Locally** — Restarts all services, runs E2E test

### Setting up a Self-Hosted Runner

Since the project runs **locally** (not in the cloud), you need a GitHub Actions self-hosted runner:

```bash
# 1. Go to your GitHub repo → Settings → Actions → Runners → New self-hosted runner

# 2. Follow the instructions to download and configure the runner
#    (Linux example — adjust for your OS)
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz
./config.sh --url https://github.com/CheikhBambaDeme/junia_mlops_project --token YOUR_TOKEN

# 3. Start the runner
./run.sh
```

Once running, any push to the trigger paths will automatically retrain and redeploy.

---

## MLflow — Experiment Tracking

All training runs are tracked with MLflow:

- **Parameters logged:** n_estimators, max_depth, random_state, test_size, dataset_rows
- **Metrics logged:** RMSE, MAE, R²
- **Artifacts logged:** serialized sklearn model

### View MLflow UI

```bash
# Install MLflow locally if not already
pip install mlflow

# Launch the UI pointing to the local tracking directory
mlflow ui --backend-store-uri ./mlruns
```

Open [http://localhost:5000](http://localhost:5000) to view experiments, compare runs, and see metrics.

---

## Data Validation

Input data is validated using **Pandera** schemas before training and inference:

### Training Data Schema
| Column       | Type    | Constraints                                |
|--------------|---------|--------------------------------------------|
| HouseID      | int     | > 0                                        |
| Location     | str     | One of: New York, Los Angeles, Chicago, Houston |
| Bedrooms     | int     | 1–10                                       |
| Bathrooms    | int     | 1–5                                        |
| SquareFeet   | int     | 100–10,000                                 |
| Price        | float   | > 0                                        |

If validation fails, the training pipeline stops and logs the exact error.

---

## Model Versioning

Models are versioned using two complementary systems:

1. **Joblib files with timestamps:**
   - `housing_price_predictor_20260215_143022.joblib` (versioned)
   - `housing_price_predictor_latest.joblib` (always points to newest)
   - `housing_price_predictor_info.joblib` (metadata: features, metrics, encoder)

2. **MLflow Model Registry:**
   - Full experiment lineage
   - Parameters, metrics, and artifacts tracked per run
   - Reproducible experiments with logged random seeds

### Explicit Save & Load

```python
# Save (in train.py)
from src.train import save_model
save_model(model, label_encoder, feature_names, metrics, model_dir, model_name)

# Load (in train.py / inference.py)
from src.train import load_model
model, feature_info = load_model(model_dir, model_name)
```

---

## Environment Variables

All configuration is managed via `.env` (see `.env.example`):

| Variable                | Default                        | Description                     |
|-------------------------|--------------------------------|---------------------------------|
| `MODEL_NAME`            | `housing_price_predictor`      | Base name for model files       |
| `MLFLOW_TRACKING_URI`   | `file:///app/mlruns`           | MLflow storage location         |
| `MLFLOW_EXPERIMENT_NAME`| `housing_price_prediction`     | MLflow experiment name          |
| `DATA_PATH`             | `/app/data/raw/house_prices.csv`| Path to training data          |
| `RANDOM_SEED`           | `42`                           | Random seed for reproducibility |
| `TEST_SIZE`             | `0.2`                          | Train/test split ratio          |
| `N_ESTIMATORS`          | `100`                          | Number of trees                 |
| `MAX_DEPTH`             | `15`                           | Max tree depth                  |
| `TRAINING_API_HOST`     | `training-service`             | Hostname for Container 1        |
| `TRAINING_API_PORT`     | `8000`                         | Port for Container 1            |
| `DJANGO_PORT`           | `8080`                         | Port for Container 2            |

---

## 4-Phase Implementation Plan

This project is designed to be implemented by a team of 4 people:

### Phase 1: Foundation & Data (Person 1)
- [x] Set up project directory structure
- [x] Download and inspect Kaggle dataset
- [x] Create `.env` / `.env.example`
- [x] Implement `src/validate_data.py` (Pandera schemas)
- [x] Implement `src/model.py` (model architecture + preprocessing)
- [x] Write initial `requirements.txt` files

### Phase 2: Training Pipeline & MLflow (Person 2)
- [x] Implement `src/train.py` (full training loop)
- [x] Set up MLflow experiment tracking
- [x] Implement explicit `save_model()` and `load_model()` functions
- [x] Implement logging to `logs/training.log`
- [x] Implement `src/inference.py` (inference wrapper with explicit loading)

### Phase 3: Containerization & API (Person 3)
- [x] Create `training-service/Dockerfile`
- [x] Implement FastAPI in `api/main.py`
- [x] Model loaded at startup via lifespan event
- [x] Create `/predict`, `/train`, `/metrics`, `/health` endpoints
- [x] Create `docker-compose.yml` with both services
- [x] Create `django-service/Dockerfile`

### Phase 4: Django Frontend & CI/CD (Person 4)
- [x] Create Django project (`housing_app`)
- [x] Implement predictor app (form, views, template)
- [x] Set up GitHub Actions workflow (`train-pipeline.yml`)
- [x] Configure triggers (model change, data change, manual)
- [x] Write comprehensive README

---

## Quick Reference

```bash
# Build and start everything
docker compose up --build

# Train the model (first time)
curl -X POST http://localhost:8000/train

# Check model metrics
curl http://localhost:8000/metrics

# Make a prediction via API
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"Bedrooms": 3, "Bathrooms": 2, "SquareFeet": 1800, "Location": "Chicago"}'

# Stop everything
docker compose down

# View logs
docker compose logs -f training-service
docker compose logs -f django-service
cat logs/training.log
```

---

## Team

- **Cheikh Bamba Deme** — Junia ISEN MLOps Project

---

## License

This project is for educational purposes (Junia ISEN MLOps course).
