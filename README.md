# Adaptive Study Planner: A Multi-Agent Concierge System

## 1. Project Overview

Adaptive Study Planner is an AI-powered academic concierge that helps students turn scattered deadlines into a personalized, conflict-free study plan.  
It uses a multi-agent architecture built on Gemini 1.5 Flash to collect tasks, generate optimized schedules, and summarize what to study next.  

This project is submitted to the **5-Day AI Agents Intensive Course with Google – Capstone Project** under the **Concierge Agents** track.  

---

## 2. Problem, Solution, and Value

### Problem

Students often juggle multiple courses, assignments, exams, and projects while relying on manual planning using calendars or to-do lists.  
This leads to inefficient schedules, last-minute cramming, and missed deadlines because traditional tools do not understand academic workload or adapt when plans change.  

### Solution

Adaptive Study Planner acts as a personal study concierge that:

- Collects academic tasks and preferences through natural language chat.  
- Automatically generates an optimized, conflict-aware study plan using code execution tools.  
- Summarizes upcoming study blocks so students always know what to work on next.  

The system combines large language models and tools to move from simple reminders to intelligent planning.  

### Value

- Reduces manual planning time by automating schedule creation and updates.  
- Helps students avoid missed deadlines through proactive, prioritized plans.  
- Adapts to user preferences and can be extended to integrate calendars or LMS systems.  

---

## 3. Track and Course Features Demonstrated

**Track:** Concierge Agents  

**Key course features implemented (3+ as required):**

1. **Multi-agent system**  
   - Root coordinator agent orchestrates three sub-agents: IntakeAgent, PlannerAgent, and ReminderAgent.  
   - Each agent has a clear role and uses tools to perform non-trivial actions.  

2. **Tools (Code execution and custom tools)**  
   - Python code execution tool runs a scheduling algorithm that creates time-blocked study plans.  
   - Custom tools manage profile preferences, task storage, and study plan storage in memory.  

3. **Sessions and memory**  
   - In-memory state (`USER_STATE`) acts as a simple session and long-term memory within the process.  
   - Stores profile, tasks, and generated plans across multiple user turns.  

4. **Observability (logging)**  
   - Logging is used around the root agent calls to trace requests and responses.  

5. **Use of Gemini**  
   - All agents are powered by Gemini 1.5 Flash via the Gemini / Google ADK stack.  

---

## 4. System Architecture

The system uses a multi-agent pattern:

- **Root Agent (Coordinator)**  
  - Receives the user’s query and decides whether to call the IntakeAgent, PlannerAgent, or ReminderAgent.  
  - Returns a final, user-friendly response.  

- **IntakeAgent**  
  - Collects course details, exams, assignments, projects, and study preferences using conversation.  
  - Converts natural language into structured JSON and calls tools:
    - `save_profile` to store study preferences.
    - `add_task` to store tasks with titles, due dates, estimates, and priorities.  

- **PlannerAgent**  
  - Fetches tasks via `list_tasks`.  
  - Calls the `python_code_execution` tool with a scheduling script and variables (`tasks`, `profile`).  
  - Reads the computed plan from the script output and calls `save_plan` to persist it.  
  - Explains the generated plan in natural language.  

- **ReminderAgent**  
  - Uses the `get_upcoming_blocks` tool to fetch near-term study blocks.  
  - Summarizes what the student should study today or in the next 24 hours.  

- **Tools and Memory**  
  - Custom tools wrap Python functions that:
    - Maintain `USER_STATE` with `profile`, `tasks`, and `plans`.
    - Provide a simple but clear example of session and state management.  

Include a diagram (for example `docs/architecture.png`) showing the user, root agent, three sub-agents, tools, and state store.  

---

## 5. Code Structure

src/
│
├─ main.py # CLI entry point to run the agent locally
├─ agents.py # (optional) Definitions of root_agent, intake_agent, planner_agent, reminder_agent
└─ tools.py # (optional) Definitions of tools and in-memory state
 
- `main.py` contains the CLI loop that lets a user interact with the root agent from the terminal.  
- `agents.py` and `tools.py` can be used to keep agent and tool logic modular and easier to read.  
- `notebooks/adaptive_study_planner_kaggle.ipynb` (if present) shows the same logic inside a Kaggle notebook environment.  

---

## 6. Setup Instructions (Local – VS Code / Terminal)

### Prerequisites

- Python 3.10 or later installed.  
- A Gemini API key from Google AI Studio.  
- Git and a terminal (PowerShell, CMD, or bash).  

### Steps

1. **Clone the repository**

git clone https://github.com/elwindainuvarghese/adaptive-study-planner.git
cd adaptive-study-planner

2. **Create and activate a virtual environment**

Windows
python -m venv .venv
.venv\Scripts\activate

macOS / Linux
python -m venv .venv
source .venv/bin/activate


3. **Install dependencies**

pip install -r requirements.txt

4. **Configure environment variables**

Create a `.env` file in the project root:


Ensure `.env` is listed in `.gitignore` so your key is never committed.  

5. **Run the CLI demo**
python src/main.py
Example interaction:

- First: describe yourself, your study preferences, and your upcoming exams and assignments.  
- Second: ask “Generate an optimized study plan for the next week.”  
- Third: ask “What should I study today evening?”  

---
## 7. Limitations and Future Work

Current limitations:

- Uses an in-memory store; state is lost when the process stops.  
- Does not yet integrate a real calendar API (e.g., Google Calendar).  
- Reminder behavior is simulated via summaries rather than real notifications.  

Planned or possible future improvements:

- Persisting state in a database or file store for long-term history.  
- Integrating Google Calendar to avoid clashes with existing events.  
- Adding study resource recommendations or focus-mode suggestions.  

---
