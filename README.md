# AeroETA

**Aircraft Trajectory and ETA Prediction from ADS-B Data**

AeroETA is a machine learning project for predicting the future trajectory of an aircraft from recent ADS-B observations.

The main idea is to use a short history of aircraft movement — position, speed, heading, vertical rate and altitude — to predict its trajectory over the following minutes.

> **ADS-B observations → trajectory history → ML model → future trajectory**

---

## Project status

🚧 **In development**

Current stage:

* [x] ADS-B data collection
* [x] Initial data exploration
* [x] Trajectory segmentation
* [x] Training window generation
* [x] Train / validation / test split
* [ ] Physical baseline evaluation
* [ ] First ML baseline
* [ ] LSTM / GRU model
* [ ] Transformer model
* [ ] Trajectory visualization
* [ ] ETA estimation
* [ ] Model serving / API

---

## Problem

Aircraft continuously transmit information about their current state through ADS-B.

A sequence of such observations contains information about how an aircraft is moving:

* geographic position;
* ground speed;
* heading;
* vertical rate;
* altitude.

AeroETA investigates whether this recent trajectory history can be used to predict the aircraft's future movement.

The first version of the project focuses on **trajectory prediction**.

ETA estimation will be introduced as a subsequent task once reliable destination information is available.

---

## Dataset

The project uses publicly available **ADS-B state-vector data from the OpenSky Network**.

The current dataset was constructed from four hourly state-vector samples:

* `2022-05-30 07:00 UTC`
* `2022-05-30 09:00 UTC`
* `2022-05-30 19:00 UTC`
* `2022-06-27 09:00 UTC`

The raw data contains aircraft state vectors sampled at approximately 10-second intervals.

Raw data is intentionally **not stored in this repository** because of its size.

---

## Data preprocessing

The preprocessing pipeline currently performs the following steps:

1. Load OpenSky state-vector CSV files.
2. Convert Unix timestamps to UTC datetimes.
3. Remove observations with missing trajectory features.
4. Remove aircraft observations marked as being on the ground.
5. Sort observations by aircraft and time.
6. Split trajectories when large temporal gaps occur.
7. Keep fixed 10-second trajectory windows.
8. Encode aircraft heading using sine and cosine.
9. Generate historical and future trajectory windows.

### Input features

Each input sequence contains **30 observations**, corresponding to 5 minutes of history.

Seven features are used:

```text
latitude
longitude
velocity
vertical rate
barometric altitude
heading sin
heading cos
```

### Prediction target

The model predicts the following **30 observations** — another 5 minutes of trajectory.

The targets are represented as changes relative to the final point of the input history:

```text
Δlatitude
Δlongitude
Δbarometric altitude
```

This relative representation reduces the dependence of the model on the absolute geographic location of an aircraft.

---

## Dataset size

The current dataset contains:

```text
861,556 trajectory windows
21,049 unique aircraft
```

Each sample has the following shape:

```text
X: (30, 7)
y: (30, 3)
```

The complete dataset therefore has:

```text
X: (861556, 30, 7)
y: (861556, 30, 3)
```

---

## Train / validation / test split

The dataset is split **by aircraft**, rather than randomly splitting individual windows.

This is important because consecutive windows from the same aircraft are highly correlated. Randomly distributing such windows between train and test could result in information leakage.

Current split:

| Dataset    | Windows | Aircraft |
| ---------- | ------: | -------: |
| Train      | 531,140 |   12,892 |
| Validation |  74,391 |    1,842 |
| Test       | 173,158 |    4,210 |

No aircraft is shared between these three subsets.

---

## Baseline

Before training neural networks, AeroETA uses a simple physics-inspired baseline.

The baseline assumes that during the prediction horizon the aircraft continues with approximately:

* constant speed;
* constant heading;
* constant vertical rate.

The purpose of the baseline is to establish a reference point against which machine learning models can be evaluated.

### Initial results

The first evaluation was performed on the validation set using the constant-velocity baseline.

| Forecast horizon | Position MAE | Altitude MAE |
| ---------------- | -----------: | -----------: |
| 1 minute         |        929 m |       51.5 m |
| 3 minutes        |      2.97 km |      186.0 m |
| 5 minutes        |      7.93 km |      452.1 m |

The results provide a reference point for evaluating machine learning models. The main objective of the next stages is to determine whether learned temporal patterns can improve trajectory prediction compared with this simple kinematic assumption.

---

## Planned models

The project will progressively compare several approaches:

### 1. Physical baseline

Constant velocity / heading / vertical-rate prediction.

### 2. Classical ML baseline

A simple machine learning model using engineered trajectory features.

### 3. LSTM / GRU

Recurrent neural networks for modelling temporal dependencies in aircraft trajectories.

### 4. Transformer

A sequence model designed to capture longer-range temporal relationships.

The models will be compared using trajectory prediction errors at different forecast horizons.

---

## Evaluation

The primary trajectory metrics will measure prediction error in physical units.

Planned evaluation horizons include:

* 1 minute;
* 3 minutes;
* 5 minutes.

Horizontal position error will be evaluated in metres, while altitude error will be evaluated in metres.

Additional metrics and visual comparisons will be added as the project develops.

---

## Project structure

```text
aviation-eta/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── notebooks/
│   └── 01_trajectory_dataset.ipynb
├── src/
│   └── analyze_opensky.py
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
└── uv.lock
```

---

## Technology

* Python 3.13
* NumPy
* pandas
* scikit-learn
* PyArrow
* Jupyter Notebook
* OpenSky Network ADS-B data

The project environment and dependencies are managed with [`uv`](https://github.com/astral-sh/uv).

---

## Roadmap

* [x] Acquire ADS-B state-vector data
* [x] Explore trajectory structure
* [x] Segment trajectories
* [x] Build 5-minute history / 5-minute forecast windows
* [x] Split data by aircraft
* [ ] Evaluate physical baseline
* [ ] Train first ML model
* [ ] Train LSTM / GRU
* [ ] Train Transformer
* [ ] Compare models
* [ ] Visualize predicted vs. actual trajectories
* [ ] Add destination-aware ETA prediction
* [ ] Build inference pipeline
* [ ] Add API / demo

---

## Data source

OpenSky Network provides open access to aircraft tracking data for research and other non-commercial purposes.

More information:

* OpenSky Network
* OpenSky Network datasets
* ADS-B state-vector data

---

## License

The project license will be added later.
