import os
from dotenv import load_dotenv

from google.adk.agents import Agent, LlmAgent
from google.adk.tools import Tool
from datetime import datetime, timedelta


# 1) Load API key from .env
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")

# 2) In-memory state (acts as simple session/memory)
USER_STATE = {
    "profile": {},
    "tasks": [],
    "plans": [],
}

def save_profile(preferences: dict) -> str:
    USER_STATE["profile"].update(preferences)
    return "Profile updated."

def add_task(task: dict) -> str:
    USER_STATE["tasks"].append(task)
    return f"Task added: {task.get('title', 'Untitled')}"

def list_tasks() -> list:
    return USER_STATE["tasks"]

def save_plan(plan: list) -> str:
    USER_STATE["plans"] = plan
    return f"Saved {len(plan)} planned study blocks."

def get_upcoming_blocks(hours_ahead: int = 24) -> list:
    now = datetime.now()
    horizon = now + timedelta(hours=hours_ahead)
    upcoming = []
    for block in USER_STATE.get("plans", []):
        start = datetime.fromisoformat(block["start"])
        if now <= start <= horizon:
            upcoming.append(block)
    return upcoming

# 3) Wrap tools
save_profile_tool = Tool(
    name="save_profile",
    description="Save or update the student's study preferences and profile.",
    func=save_profile,
)

add_task_tool = Tool(
    name="add_task",
    description="Add a new academic task (exam, assignment, project).",
    func=add_task,
)

list_tasks_tool = Tool(
    name="list_tasks",
    description="Return all known tasks.",
    func=list_tasks,
)

save_plan_tool = Tool(
    name="save_plan",
    description="Persist generated study plan blocks.",
    func=save_plan,
)

get_upcoming_blocks_tool = Tool(
    name="get_upcoming_blocks",
    description="Return upcoming study blocks within a given time horizon in hours.",
    func=get_upcoming_blocks,
)

# 4) Python scheduling logic used by planner via code execution
def generate_schedule(tasks, profile):
    """Generate a simple time-blocked study plan."""
    daily_start = profile.get("daily_start_hour", 8)
    daily_end = profile.get("daily_end_hour", 22)
    max_session = profile.get("max_session_minutes", 50)

    now = datetime.now()
    sorted_tasks = sorted(
        tasks,
        key=lambda t: (datetime.fromisoformat(t["due"]), -t.get("priority", 3))
    )

    plan = []
    current = now

    for task in sorted_tasks:
        remaining = float(task.get("estimated_hours", 1.0)) * 60.0
        due = datetime.fromisoformat(task["due"])

        while remaining > 0 and current < due:
            if current.hour < daily_start:
                current = current.replace(hour=daily_start, minute=0, second=0, microsecond=0)
            elif current.hour >= daily_end:
                current = (current + timedelta(days=1)).replace(
                    hour=daily_start, minute=0, second=0, microsecond=0
                )

            session_minutes = min(max_session, remaining)
            end = current + timedelta(minutes=session_minutes)

            if end > due:
                break

            block = {
                "title": task["title"],
                "subject": task.get("subject", ""),
                "start": current.isoformat(),
                "end": end.isoformat(),
                "minutes": session_minutes,
            }
            plan.append(block)

            remaining -= session_minutes
            current = end + timedelta(minutes=10)

    return plan


schedule_tool = Tool(
    name="generate_schedule",
    description="Generate an optimized study plan from tasks and profile preferences.",
    func=generate_schedule,
)

# 5) Define sub-agents

intake_agent = LlmAgent(
    name="intake_agent",
    model="gemini-1.5-flash",
    instruction=(
        "You are an intake assistant for an Adaptive Study Planner.\n"
        "Collect courses, exams, assignments, projects, and study preferences.\n"
        "Convert the user's input into structured JSON and call save_profile/add_task.\n"
        "Always confirm what you saved."
    ),
    tools=[save_profile_tool, add_task_tool, list_tasks_tool],
)

planner_agent = LlmAgent(
    name="planner_agent",
    model="gemini-1.5-flash",
    instruction=(
        "You are a study planner.\n"
        "1) Call list_tasks to get tasks.\n"
        "2) Use the python_code_execution tool with 'tasks' and 'profile' variables.\n"
        "3) Read 'result' from the executed code as the study plan.\n"
        "4) Call save_plan to store it.\n"
        "5) Explain the plan to the user clearly."
    ),
   tools=[list_tasks_tool, save_profile_tool, save_plan_tool, schedule_tool],

)
reminder_agent = LlmAgent(
    name="reminder_agent",
    model="gemini-1.5-flash",
    instruction=(
    "You are a study planner agent.\n"
    "1) Call list_tasks to get all tasks.\n"
    "2) Call generate_schedule tool with the tasks and the user's profile.\n"
    "3) Take the returned list of study blocks and call save_plan to store it.\n"
    "4) Explain the plan to the user clearly."
),
    tools=[get_upcoming_blocks_tool],
)

root_agent = Agent(
    name="adaptive_study_planner_root",
    model="gemini-1.5-flash",
    description="Root coordinator for the multi-agent Adaptive Study Planner.",
    instruction=(
        "Route requests:\n"
        "- To intake_agent when user is describing tasks or preferences.\n"
        "- To planner_agent when the user wants a plan.\n"
        "- To reminder_agent when the user asks what to study now/today.\n"
        "Return a clear final answer."
    ),
    subagents=[intake_agent, planner_agent, reminder_agent],
)

def main():
    print("Adaptive Study Planner – CLI demo")
    print("Type 'exit' to quit.\n")

    while True:
        prompt = input("You: ")
        if prompt.lower().strip() in {"exit", "quit"}:
            break
        response = root_agent.run(prompt)
        print("\nAgent:\n", response, "\n")

if __name__ == "__main__":
    main()
# End of main.py
