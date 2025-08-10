"""
Customer Support Agent with OpenAI Agents SDK
Backend function: support_agent_backend
"""

import os
from typing import Dict
from dotenv import load_dotenv
from flask import flash
from openai import OpenAI
from openai.agents import Agent, Tool, run_agents

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Missing OPENAI_API_KEY in .env")

client = OpenAI(api_key=api_key)

# FAQ Database
FAQ_KB = {
    "pricing": "Our pricing is subscription-based with monthly and annual options.",
    "features": "We provide AI chatbots, RAG search, multi-agent orchestration, and integrations.",
    "support": "Support is available 24/7 via email and live chat."
}

# --- Define Tools/Agents ---

# Classification agent
classification_agent = Agent(
    name="classifier",
    instructions="You are a customer support triage AI. Respond with exactly one category word: Pricing, Features, Support, or Other.",
    model="gpt-4o-mini"
)

# Fallback answer agent
fallback_agent = Agent(
    name="responder",
    instructions="You are a helpful support assistant. Provide concise, polite answers to queries.",
    model="gpt-4o-mini"
)

# FAQ lookup tool
def faq_lookup(query: str, category: str) -> str:
    cat_norm = category.lower()
    if cat_norm in FAQ_KB:
        return FAQ_KB[cat_norm]
    return None

faq_tool = Tool(
    name="FAQ Lookup",
    description="Lookup frequently asked questions by category.",
    func=faq_lookup
)

def support_agent_backend(request) -> Dict:
    context = {}
    if request.method == "POST":
        user_query = request.form.get("user_query", "").strip()
        if not user_query:
            context["support_response"] = "Please enter your question."
            return context

        # Step 1: Classify
        classification_resp = classification_agent.run(user_query)
        category = classification_resp.output_text.strip()

        # Step 2: Try FAQ
        faq_ans = faq_lookup(user_query, category)
        if faq_ans:
            answer = faq_ans
        else:
            # Step 3: Use fallback responder
            answer = fallback_agent.run(user_query).output_text.strip()

        context["support_response"] = f"**Category:** {category}\n\n**Answer:** {answer}"

    return context