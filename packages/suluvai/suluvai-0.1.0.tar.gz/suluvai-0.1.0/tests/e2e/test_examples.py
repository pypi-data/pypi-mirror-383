"""
End-to-End Tests: Examples
Tests that all example files run successfully
Developed by SagaraGlobal
"""
import pytest
import os
import subprocess
from pathlib import Path

skip_if_no_key = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set"
)


class TestExamples:
    """Test all example files"""
    
    @skip_if_no_key
    def test_simple_agent_example(self):
        """Test examples/simple_agent.py runs successfully"""
        result = subprocess.run(
            ["python", "examples/simple_agent.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode == 0
        assert "✅ Done!" in result.stdout or "116" in result.stdout
    
    @skip_if_no_key
    @pytest.mark.slow
    def test_streaming_example(self):
        """Test examples/streaming_example.py runs successfully"""
        result = subprocess.run(
            ["python", "examples/streaming_example.py"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        assert result.returncode == 0
        assert "Streaming Example" in result.stdout
    
    @skip_if_no_key
    @pytest.mark.slow
    def test_workflow_example(self):
        """Test examples/workflow_example.py runs successfully"""
        result = subprocess.run(
            ["python", "examples/workflow_example.py"],
            capture_output=True,
            text=True,
            timeout=90
        )
        
        assert result.returncode == 0
        assert "Workflow Example" in result.stdout


class TestImports:
    """Test that all imports work"""
    
    def test_import_all(self):
        """Test importing all main components"""
        from suluvai import (
            create_agent,
            AgentConfig,
            SuluvAIState,
            SubAgent,
            WorkflowBuilder,
            LocalFileStorage,
            VirtualStorage,
            ConversationMemory,
            WorkingMemory,
            stream_agent
        )
        
        assert create_agent is not None
        assert AgentConfig is not None
        assert WorkflowBuilder is not None
    
    def test_version(self):
        """Test version is correct"""
        import suluvai
        assert suluvai.__version__ == "0.1.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
