## DAY 1: 

- Goal: User selects predefined components and generates basic components

// Tools
- React / Vite for the frontend
- React Flow for the wiring diagram canvas
- FastAPI for the backend API
- Pydantic for backend request and response validation
- Tailwind CSS for frontend styling
- Uvicorn to run the FastAPI backend locally

/ ARCHITECTURE:
The user selects components in the React frontend. The selected component IDs are sent to the FastAPI backend through a POST request. The backend checks the selected components, applies existing wiring rules, and returns nodes, edges, and warnings. The frontend then renders the result using React Flow.



Failure:

Hardcoded components had weird wiring - so color coded and bolded
Components pin outputs were weird not in frame - used a scaling algorithm 

## DAY 2: