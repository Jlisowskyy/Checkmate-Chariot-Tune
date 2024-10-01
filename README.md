# Checkmate-Chariot-Tune

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
3. [Usage](#usage)
    - [Worker Usage](#worker)
    - [Manager Usage](#manager)
4. [Details](#details)
5. [Roadmap](#roadmap)
6. [License](#license)

## Introduction

**Checkmate-Chariot-Tune** is a project designed to train and optimize the parameters of chess algorithms. Initially, it was developed to tune the **Checkmate-Chariot** chess engine, but the system is designed to be adaptable for tuning any chess engine. The project plans to integrate various optimization methods, including traditional tuning algorithms as well as advanced machine learning (ML) techniques. 

In the future, this tool will support tuning via neural networks (NNUE) and other ML models, making it a powerful solution for engine performance optimization.

## Getting Started

### Prerequisites

To set up the project, ensure you have the following dependencies:
- Python 3.12 or higher
- Python virtual environment (`virtualenv`) for dependency management (recommended)

### Installation

#### For Worker and Manager Components

1. Clone the repository:
    ```bash
    git clone https://github.com/Jlisowskyy/Checkmate-Chariot-Tune
    cd Checkmate-Chariot-Tune
    ```

2. Deploy the worker or manager components based on your operating system.

**For Unix systems:**
```bash
./Worker/deploy.sh
```
or
```bash
./Manager/deploy.sh
```

**For Windows systems:**
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r Worker\requirements.txt
pip install -r Manager\requirements.txt
```

#### For Frontend Component

Frontend installation steps are still under development.
```shell
TBD
```

## Usage

### Worker

To access help for the Worker CLI:
```shell
python worker_cli.py --help
```

To deploy a worker:
```shell
python worker_cli.py --deploy
```

To connect a deployed worker to the manager:
```shell
python worker_cli.py --connect host=http://127.0.0.1:8000 name=worker1
```

### Manager

**For Unix systems:**
```bash
./Manager/run.sh
```

**For Windows systems:**
```powershell
TBD
```

## Details

Detailed documentation on the internal workings and architecture of the system will be provided in future updates. This section will cover:
- How tasks are created, assigned, and managed.
- Communication protocols between Manager and Worker.
- Tuning methodology and algorithms used for optimizing engines.

## Roadmap

The project follows a structured roadmap with completed features as well as future goals:

- **Worker Components:**
  - [x] Worker CLI
  - [x] Worker registration and connection to Manager
  - [ ] Worker task receiving and configuration
  - [ ] Worker task job execution
  - [ ] Worker task progress hardening

- **Manager Components:**
  - [x] Manager modules
  - [x] Manager <-> Worker communication
  - [x] Task creation and management
  - [x] Task job dispatching
  - [ ] State and progress hardening
  - [x] Worker management

- **Frontend:**
  - [ ] Task creation and management
  - [ ] Worker management interface
  - [x] Frontend API

- **Tuning Modules:**
  - [x] Cutechess tuning module
  - [x] Checkmate-Chariot engine module
  - [x] Basic tuning methods
  - [ ] Machine Learning (ML) tuning methods
  - [ ] NNUE tuning methods

## License

This project is distributed under the MIT License. See `LICENSE.txt` for more information.