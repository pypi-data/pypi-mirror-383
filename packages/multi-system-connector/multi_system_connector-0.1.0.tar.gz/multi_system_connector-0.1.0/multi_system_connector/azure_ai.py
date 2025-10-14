# multi_system_connector/azure_ai.py

from azure.ai.projects import AIProjectClient
from azure.identity import ClientSecretCredential
from azure.ai.agents.models import ListSortOrder
from .utils import AZURE_AI_CONFIG

def query_azure_ai_assistant(utterance: str, entities: dict = None):
    try:
        credential = ClientSecretCredential(
            tenant_id=AZURE_AI_CONFIG["tenant_id"],
            client_id=AZURE_AI_CONFIG["client_id"],
            client_secret=AZURE_AI_CONFIG["client_secret"]
        )
        project = AIProjectClient(credential=credential, endpoint=AZURE_AI_CONFIG["project_endpoint"])
        agent = project.agents.get_agent(AZURE_AI_CONFIG["agent_id"])
        thread = project.agents.threads.create()

        context = ""
        if entities:
            context_parts = [f"{k}: {v}" for k, v in entities.items()]
            context = "Context: " + ", ".join(context_parts) + "\n"

        message = project.agents.messages.create(thread_id=thread.id, role="user", content=context + utterance)
        run = project.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

        if run.status == "failed":
            return {"status": "error", "error": run.last_error}

        messages = project.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        response_text = ""
        for msg in messages:
            if msg.role == "assistant" and msg.text_messages:
                response_text = msg.text_messages[-1].text.value

        return {"response": response_text, "thread_id": thread.id, "run_id": run.id}

    except Exception as e:
        return {"status": "error", "error": str(e)}
