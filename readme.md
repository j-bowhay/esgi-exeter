# ESGI 195 Exeter — Floor Plan Graph Analysis

Computational tools developed for the ESGI Exeter project on analysing graph-theoretic properties of floor plans to support the processing of planning applications.

> **Status:** Working research prototype produced during ESGI 195. Please check the notes below before using this repository on any new data.

## 📌 Overview

This repository contains Python and notebook-based workflows for processing floor-plan outputs, constructing or analysing graph representations, and inspecting graph overlays and room-mask visualisations.

The work is associated with the IEG Group challenge at the 195th European Study Group with Industry (ESGI 195), hosted at the University of Exeter on 20–24 July 2026, entitled **“Analysing graph theoretic properties of floor plans to improve processing of planning applications.”**

The current repository is intentionally lightweight (mid-week reporting stage) and includes:

- `floorplans3.ipynb` — exploratory analysis and visualisation notebook.
- `process_data.py` — Python data-processing script.
- `readme.md` — original minimal data-layout notes.
- `.gitignore` — repository ignore rules.

## ✅ Features

- Load processed floor-plan data from a local `data/` directory.
- Work with graph outputs stored as JSON.
- Inspect generated graph overlays on the input floor plan image.
- Inspect generated graph overlays on room-mask images.
- Support exploratory analysis through a Jupyter notebook workflow.
- Provide a starting point for graph-theoretic metrics, validation, and downstream reporting.

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/j-bowhay/esgi-exeter.git
cd esgi-exeter
```

### 2. Create a Python environment

A dedicated environment is recommended. For example, using `venv`:

```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate       # Windows PowerShell
```

### 3. Install dependencies

A dependency file is not currently present in the repository. Until one is added, install the packages required by the notebook and processing script manually. A likely starting point is:

```bash
pip install numpy pandas matplotlib networkx pillow opencv-python jupyter
```

If the notebook imports additional packages, install them as needed and consider recording them in a `requirements.txt` file.

## 📁 Data Layout

Place floor-plan data inside a top-level `data/` directory. The current expected layout is:

```text
data/
└── 10108/
    ├── graph_output.json
    └── output/
        ├── graph_on_input.png
        ├── graph_on_room_masks.png
        ├── input.png
        └── model_processed.pkl
```

Each subdirectory under `data/` should correspond to one floor-plan case or sample identifier.

### Expected files

| File | Description |
|---|---|
| `graph_output.json` | Graph representation or graph-derived output for the floor plan. |
| `output/input.png` | Input image used for processing or inspection. |
| `output/graph_on_input.png` | Visual overlay of the graph on the original input image. |
| `output/graph_on_room_masks.png` | Visual overlay of the graph on room-mask outputs. |
| `output/model_processed.pkl` | Pickled processed model object or intermediate output. |

> **Note:** Large, private, or commercially sensitive data should not be committed to the repository. Keep local data in `data/` and use `.gitignore` rules to prevent accidental commits.

## ⚙️ Running the Workflow

### Option A — Notebook workflow

Launch Jupyter and open the analysis notebook:

```bash
jupyter notebook floorplans3.ipynb
```

Then update any paths or case identifiers inside the notebook to point to your local `data/` directory.

### Option B — Scripted processing

Run the processing script from the repository root:

```bash
python process_data.py
```

## 📊 Outputs

Depending on the current processing path, the workflow may produce or consume:

- graph-structured floor-plan data in JSON format;
- image overlays of graph nodes and edges on the original floor plan;
- image overlays on room-mask representations;
- tables or figures for graph-theoretic summaries.

More suggested graph metrics to document as the project matures include:

- number of rooms or regions;
- number of graph nodes and edges;
- connected components;
- degree distribution;
- centrality measures;
- shortest-path or accessibility metrics;
- plan-level consistency or anomaly indicators.

## 📂 Repository Structure

```text
.
├── .gitignore
├── floorplans3.ipynb       # exploratory notebook for floor-plan graph analysis
├── process_data.py         # data processing script
├── readme.md               # original minimal notes
└── data/                   # local data directory; usually not committed
    └── <case_id>/
        ├── graph_output.json
        └── output/
            ├── graph_on_input.png
            ├── graph_on_room_masks.png
            ├── input.png
            └── model_processed.pkl
```

## 📚 Citation

A technical report (as per ESGI tradition) will accompany this report several weeks after completion, with this repository linked to the respective primary output. There are several other contributions building towards the same output, including:
- [the implementation](https://github.com/emmashelley/ESGI/tree/main) built by Emma Shelley
- [the code](https://github.com/SimonRBlackburn/ESGI-Exeter-2026) built by Simon Blackburn
  
all building together towards a streamlined workflow in our problem space.
