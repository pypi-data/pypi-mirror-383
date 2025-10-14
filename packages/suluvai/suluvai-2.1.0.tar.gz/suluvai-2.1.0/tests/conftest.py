"""
Pytest configuration and fixtures
Developed by SagaraGlobal
"""
import pytest
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Skip marker for tests requiring OpenAI API key
skip_if_no_key = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set - skipping LLM tests"
)


@pytest.fixture
def openai_key():
    """Fixture to get OpenAI API key"""
    return os.getenv("OPENAI_API_KEY")


@pytest.fixture
def has_openai_key():
    """Check if OpenAI key is available"""
    return bool(os.getenv("OPENAI_API_KEY"))
