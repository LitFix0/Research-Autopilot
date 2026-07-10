import json
from crewai import Crew, Task, Process
from core.config import MAX_RETRY_LOOPS, OUTPUT_DIR
from core.agents import build_all_agents
from core.tools import get_search_tool
from core.memory import (
    init_db, create_session, close_session,
    save_agent_output, save_search_results
)
import os


def build_planner_task(planner, query: str) -> Task:
    return Task(
        description=(
            f"The user wants to research the following topic:\n\n"
            f"'{query}'\n\n"
            f"Break this into exactly 3 focused sub-questions. "
            f"Return them as a numbered list, one per line. "
            f"Each sub-question must be specific and searchable."
        ),
        expected_output=(
            "A numbered list of exactly 3 sub-questions. Example:\n"
            "1. What is X?\n"
            "2. How does X work?\n"
            "3. What are the latest developments in X?"
        ),
        agent=planner,
    )


def build_searcher_task(searcher, sub_question: str, planner_task: Task) -> Task:
    return Task(
        description=(
            f"Search the web and answer this sub-question:\n\n"
            f"'{sub_question}'\n\n"
            f"Use the web_search tool to find relevant results. "
            f"Return a structured summary with key facts and source URLs."
        ),
        expected_output=(
            "A structured summary with:\n"
            "- Key facts (bullet points)\n"
            "- Source URLs cited inline\n"
            "- A 2-3 sentence conclusion"
        ),
        agent=searcher,
        tools=[get_search_tool()],
        context=[planner_task],
    )


def build_synthesizer_task(synthesizer, searcher_tasks: list) -> Task:
    return Task(
        description=(
            "You have received research findings from multiple searcher agents. "
            "Merge all findings into a single, well-structured markdown report. "
            "Include: an executive summary, key findings by theme, and a sources section. "
            "Remove duplicates and resolve any contradictions."
        ),
        expected_output=(
            "A complete markdown report with:\n"
            "# Title\n"
            "## Executive Summary\n"
            "## Key Findings\n"
            "## Sources"
        ),
        agent=synthesizer,
        context=searcher_tasks,
    )


def build_critic_task(critic, synthesizer_task: Task) -> Task:
    return Task(
        description=(
            "Review the synthesized research report critically. "
            "Check for: unsupported claims, missing perspectives, weak sources, "
            "logical gaps, or areas needing more research. "
            "Respond with ONLY a JSON object in this exact format:\n"
            '{"approved": true/false, "feedback": ["issue 1", "issue 2"]}'
        ),
        expected_output='{"approved": true, "feedback": []}',
        agent=critic,
        context=[synthesizer_task],
    )


def parse_critic_output(raw: str) -> dict:
    """Safely extract JSON from critic output."""
    try:
        start = raw.index("{")
        end   = raw.rindex("}") + 1
        return json.loads(raw[start:end])
    except Exception:
        return {"approved": True, "feedback": []}


def extract_sub_questions(planner_output: str) -> list:
    """Pull the 3 numbered sub-questions from planner output."""
    lines = planner_output.strip().splitlines()
    questions = []
    for line in lines:
        line = line.strip()
        if line and line[0].isdigit() and "." in line:
            questions.append(line.split(".", 1)[1].strip())
    return questions[:3] if questions else [planner_output]


def save_report(query: str, report: str) -> str:
    """Write the final markdown report to disk."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in query)[:50]
    filepath  = os.path.join(OUTPUT_DIR, f"{safe_name}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)
    return filepath


def run_pipeline(query: str) -> str:
    """
    Main entry point. Runs the full research pipeline and
    returns the path to the saved report.
    """
    init_db()
    session_id  = create_session(query)
    agents      = build_all_agents()
    planner     = agents["planner"]
    searchers   = agents["searchers"]
    synthesizer = agents["synthesizer"]
    critic      = agents["critic"]

    report   = ""
    approved = False
    loop     = 0

    while not approved and loop < MAX_RETRY_LOOPS:
        loop += 1
        print(f"\n[crew] Pipeline run {loop}/{MAX_RETRY_LOOPS}")

        # Step 1: Plan
        planner_task = build_planner_task(planner, query)
        plan_crew    = Crew(agents=[planner], tasks=[planner_task],
                            process=Process.sequential, verbose=True)
        planner_output = str(plan_crew.kickoff())
        save_agent_output(session_id, "planner", planner_output)
        sub_questions = extract_sub_questions(planner_output)
        print(f"[crew] Sub-questions: {sub_questions}")

        # Step 2: Search
        searcher_tasks = [
            build_searcher_task(searchers[i], sub_questions[i], planner_task)
            for i in range(min(len(sub_questions), len(searchers)))
        ]
        search_crew = Crew(agents=searchers, tasks=searcher_tasks,
                           process=Process.sequential, verbose=True)
        search_crew.kickoff()
        for i, task in enumerate(searcher_tasks):
            output = str(task.output) if task.output else ""
            save_agent_output(session_id, f"searcher_{i+1}", output)
            save_search_results(session_id, sub_questions[i], [output])

        # Step 3: Synthesize
        synth_task = build_synthesizer_task(synthesizer, searcher_tasks)
        synth_crew = Crew(agents=[synthesizer], tasks=[synth_task],
                          process=Process.sequential, verbose=True)
        report = str(synth_crew.kickoff())
        save_agent_output(session_id, "synthesizer", report)

        # Step 4: Critic
        critic_task = build_critic_task(critic, synth_task)
        critic_crew = Crew(agents=[critic], tasks=[critic_task],
                           process=Process.sequential, verbose=True)
        critic_output = str(critic_crew.kickoff())
        save_agent_output(session_id, "critic", critic_output)

        verdict  = parse_critic_output(critic_output)
        approved = verdict.get("approved", True)
        feedback = verdict.get("feedback", [])

        if approved:
            print("[crew] Critic approved the report.")
        else:
            print(f"[crew] Critic rejected. Feedback: {feedback}")
            if loop < MAX_RETRY_LOOPS:
                query = query + f"\n\nPrevious feedback to address: {'; '.join(feedback)}"

    filepath = save_report(query, report)
    close_session(session_id)
    print(f"[crew] Report saved to: {filepath}")
    return filepath