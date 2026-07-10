import os
from crewai import Agent
from crewai.llm import LLM
from core.config import GROQ_API_KEY, GROQ_MODEL, NUM_SEARCHER_AGENTS

# Disable LiteLLM caching globally via env var — avoids the cache=False bool bug
os.environ["GROQ_API_KEY"]        = GROQ_API_KEY
os.environ["LITELLM_CACHE"]       = "false"
os.environ["LITELLM_LOCAL_CACHE"] = "false"


def get_llm() -> LLM:
    return LLM(
        model=f"groq/{GROQ_MODEL}",
        temperature=0.3,
        # no cache param here — controlled via env vars above
    )


def make_planner() -> Agent:
    return Agent(
        role="Research Planner",
        goal=(
            "Break the user's research query into 3 focused, non-overlapping "
            "sub-questions that together cover the topic comprehensively."
        ),
        backstory=(
            "You are a senior research strategist. You excel at decomposing "
            "broad topics into precise sub-questions that can be independently "
            "searched and later synthesized into a cohesive report."
        ),
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )


def make_searcher(index: int) -> Agent:
    return Agent(
        role=f"Web Researcher {index}",
        goal=(
            "Search the web for your assigned sub-question and return a "
            "structured summary with key facts and source URLs."
        ),
        backstory=(
            f"You are research agent #{index}, specialised in finding accurate, "
            "up-to-date information on the web. You always cite your sources "
            "and separate facts from opinions."
        ),
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )


def make_synthesizer() -> Agent:
    return Agent(
        role="Research Synthesizer",
        goal=(
            "Merge the findings from all searcher agents into a single, "
            "well-structured markdown report. Remove duplicates, resolve "
            "contradictions, and ensure logical flow."
        ),
        backstory=(
            "You are a senior analyst and science writer. You transform raw "
            "research notes into clear, insightful reports that a non-expert "
            "can understand. You are rigorous about attribution and accuracy."
        ),
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )


def make_critic() -> Agent:
    return Agent(
        role="Research Critic",
        goal=(
            "Review the synthesized report for gaps, weak sources, unsupported "
            "claims, or missing perspectives. Output a JSON object with two keys: "
            "'approved' (true/false) and 'feedback' (list of issues to fix)."
        ),
        backstory=(
            "You are a rigorous peer reviewer with high standards. You flag "
            "vague claims, missing data, and one-sided arguments. If the report "
            "meets quality standards you approve it; otherwise you return "
            "actionable feedback for revision."
        ),
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )


def build_all_agents() -> dict:
    return {
        "planner":     make_planner(),
        "searchers":   [make_searcher(i + 1) for i in range(NUM_SEARCHER_AGENTS)],
        "synthesizer": make_synthesizer(),
        "critic":      make_critic(),
    }


if __name__ == "__main__":
    agents = build_all_agents()
    print("Agents loaded:")
    print(f"  planner     : {agents['planner'].role}")
    for s in agents["searchers"]:
        print(f"  searcher    : {s.role}")
    print(f"  synthesizer : {agents['synthesizer'].role}")
    print(f"  critic      : {agents['critic'].role}")