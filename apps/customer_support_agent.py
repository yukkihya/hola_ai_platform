"""
Customer Support Agentic AI (CrewAI + OpenAI)
Backend function: support_agent_backend
"""

import os
from typing import Dict
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from flask import flash
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()
#OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
#if not OPENAI_API_KEY:
    #raise ValueError("OPENAI_API_KEY not found in .env file.")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in .env file.")
# Define FAQ KB
FAQ_KB = {
    "pricing": "Our pricing is subscription-based with monthly and annual options. Discounts apply for yearly plans.",
    "features": "We offer AI chatbots, RAG search, multi-agent workflows, and integrations with Slack and email.",
    "support": "You can reach us 24/7 via in-app chat or email support@example.com."
}
'''
# Initialize OpenAI LLM for CrewAI
openai_llm = LLM(
    model="gpt-4o-mini",        # Can change to gpt-4o for more complex reasoning
    api_key=OPENAI_API_KEY,
    temperature=0.3
)
openai_llm = ChatGroq(
    temperature=0,
    #model_name="llama3-70b-8192",
    model_name="mixtral-8x7b-32768"
)
'''
openai_llm =LLM(
    model="openrouter/meta-llama/llama-3.3-70b-instruct",  # or any other model listed on OpenRouter
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",  # crucial for routing through OpenRouter
    temperature=0.3,
    litellm_provider="openrouter" 
)


# Define Agents
classifier_agent = Agent(
    role="Query Classifier",
    goal="Classify customer questions into: Pricing, Features, Support, or Other.",
    backstory=(
        "You are an expert at quickly categorizing customer support queries "
        "to route them to the correct department."
    ),
    llm=openai_llm,
    verbose=False
)

responder_agent = Agent(
    role="Customer Support Responder",
    goal="Give helpful, concise, and accurate answers to customer questions.",
    backstory=(
        "You are a knowledgeable support rep with access to product details, "
        "pricing, features, and escalation procedures."
    ),
    llm=openai_llm,
    verbose=False
)

# Flask backend function
def support_agent_backend(request) -> Dict:
    context = {}
    if request.method == "POST":
        user_query = request.form.get("user_query", "").strip()
        if not user_query:
            context["support_response"] = "Please enter your question."
            return context

        # Create Crew with sequential tasks
        classification_task = Task(
            description=f"Classify this query: '{user_query}'",
            expected_output="One word: Pricing, Features, Support, or Other.",
            agent=classifier_agent
        )

        classification_result = Crew(agents=[classifier_agent], tasks=[classification_task]).kickoff()
        
        category = classification_result.raw.strip().lower()

        # Respond based on category
        if category in FAQ_KB:
            answer = FAQ_KB[category]
        else:
            response_task = Task(
                description=f"Answer this customer query helpfully: '{user_query}'",
                expected_output="A concise and polite support answer.",
                agent=responder_agent
            )
            answer = Crew(agents=[responder_agent], tasks=[response_task]).kickoff()
            try:
                answer = answer.raw
            except:
                pass

        # Save to context for template rendering
        context["support_response"] = f"**Category:** {category.capitalize()}\n\n**Answer:** {answer}"

    return context