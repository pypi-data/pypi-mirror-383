"""
LangSmith tracing configuration for SuluvAI
Enables monitoring, debugging, and evaluation of agent runs
"""

import os
import warnings
from typing import Optional

# Suppress LangSmith warnings if not configured
warnings.filterwarnings('ignore', message='.*langsmith.*')
warnings.filterwarnings('ignore', message='.*LangSmith.*')


def enable_langsmith_tracing(
    project_name: str = "suluvai-agents",
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None
):
    """
    Enable LangSmith tracing for all agent executions.
    
    Args:
        project_name: Name of the LangSmith project (default: "zita-agents")
        api_key: LangSmith API key (defaults to LANGSMITH_API_KEY env var)
        endpoint: LangSmith API endpoint (defaults to LANGSMITH_ENDPOINT env var)
    
    Usage:
        from zita_agents.tracing import enable_langsmith_tracing
        
        enable_langsmith_tracing(
            project_name="sap-chatbot-prod",
            api_key="your-api-key-here"
        )
        
        # Now all agent.invoke() calls will be traced
        agent = create_zita_agent(...)
        result = agent.invoke(state)  # This will be traced!
    
    Environment Variables:
        LANGSMITH_API_KEY: Your LangSmith API key
        LANGSMITH_ENDPOINT: LangSmith API endpoint (optional)
        LANGCHAIN_TRACING_V2: Set to "true" to enable tracing
        LANGCHAIN_PROJECT: Project name for organizing traces
    
    Example .env file:
        LANGSMITH_API_KEY=lsv2_pt_abc123...
        LANGCHAIN_TRACING_V2=true
        LANGCHAIN_PROJECT=sap-chatbot
    """
    
    # Set LangSmith API key
    if api_key:
        os.environ["LANGSMITH_API_KEY"] = api_key
    elif not os.getenv("LANGSMITH_API_KEY"):
        print("⚠️  Warning: LANGSMITH_API_KEY not set. Tracing will not work.")
        print("   Get your API key from: https://smith.langchain.com/settings")
        return False
    
    # Set endpoint if provided
    if endpoint:
        os.environ["LANGSMITH_ENDPOINT"] = endpoint
    
    # Enable tracing
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = project_name
    
    print(f"✅ LangSmith tracing enabled")
    print(f"   Project: {project_name}")
    print(f"   View traces at: https://smith.langchain.com/")
    
    return True


def disable_langsmith_tracing():
    """
    Disable LangSmith tracing.
    
    Usage:
        from zita_agents.tracing import disable_langsmith_tracing
        
        disable_langsmith_tracing()
    """
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    print("❌ LangSmith tracing disabled")


def configure_tracing_from_env():
    """
    Auto-configure LangSmith tracing from environment variables.
    
    This is called automatically when importing suluvai if LANGCHAIN_TRACING_V2=true.
    
    Returns:
        bool: True if tracing is enabled, False otherwise
    """
    try:
        if os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true":
            project = os.getenv("LANGCHAIN_PROJECT", "suluvai-agents")
            api_key = os.getenv("LANGSMITH_API_KEY")
            
            if api_key:
                print(f"✅ LangSmith tracing auto-configured from environment")
                print(f"   Project: {project}")
                return True
            else:
                # Silently disable if no API key
                os.environ["LANGCHAIN_TRACING_V2"] = "false"
                return False
        
        # Ensure tracing is disabled if not explicitly enabled
        if "LANGCHAIN_TRACING_V2" not in os.environ:
            os.environ["LANGCHAIN_TRACING_V2"] = "false"
        
        return False
    except Exception:
        # Silently fail and disable tracing
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        return False


def get_trace_url(run_id: str) -> str:
    """
    Get the LangSmith URL for a specific trace.
    
    Args:
        run_id: The run ID from agent execution
    
    Returns:
        URL to view the trace in LangSmith
    """
    return f"https://smith.langchain.com/public/{run_id}/r"


# Auto-configure on import if env vars are set
if os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true":
    configure_tracing_from_env()
