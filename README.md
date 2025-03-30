# Axkan II Backend

A FastAPI-based backend for the Axkan II card game.

## Project Structure

```
axkan_ii_backend/
├── enums/                    # Game-related enums
│   ├── __init__.py
│   ├── game_phase.py
│   ├── game_state.py
│   ├── game_action.py
│   ├── game_status.py
│   └── player_role.py
├── game_state_manager.py     # Game state management
├── requirements.txt          # Project dependencies
└── README.md                # This file
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
uvicorn main:app --reload
```

## Game State Machine

The game follows a state machine with the following phases:
- Lobby
- Game Start
- First Turn
- Odd Turns (3,5,7)
- Even Turns (2,4,6)
- Last Turn
- Game End

Each phase has specific states and valid transitions. 