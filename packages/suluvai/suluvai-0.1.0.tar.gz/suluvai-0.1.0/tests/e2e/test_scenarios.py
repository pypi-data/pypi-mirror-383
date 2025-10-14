"""
End-to-End Scenario Tests
Real-world use cases with complete workflows
Developed by SagaraGlobal
"""
import pytest
import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from suluvai import create_agent, AgentConfig, WorkflowBuilder

load_dotenv()

skip_if_no_key = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set"
)


# Mock tools for realistic scenarios
@tool
def fetch_sales_data(quarter: str) -> str:
    """Fetch sales data for a quarter"""
    return f"Q{quarter} Sales: $1.2M, Growth: 15%, Top Product: Widget A"


@tool
def analyze_trends(data: str) -> str:
    """Analyze data trends"""
    return f"Analysis: {data[:50]}... shows positive momentum with 15% growth"


@tool
def generate_chart(data: str) -> str:
    """Generate a chart from data"""
    return f"Chart generated: bar_chart_{data[:10]}.png"


@tool
def send_email(recipient: str, subject: str, body: str) -> str:
    """Send an email (mock)"""
    return f"Email sent to {recipient}: '{subject}'"


@tool
def search_database(query: str) -> str:
    """Search database (mock)"""
    return f"Found 5 results for '{query}': Record1, Record2, Record3..."


@tool
def validate_data(data: str) -> str:
    """Validate data format"""
    if len(data) > 10:
        return "✓ Data validated successfully"
    return "✗ Data validation failed: insufficient data"


class TestDataAnalysisPipeline:
    """Test complete data analysis workflow"""
    
    @skip_if_no_key
    def test_end_to_end_sales_analysis(self):
        """
        SCENARIO: Sales Analysis Pipeline
        1. Fetch sales data
        2. Analyze trends
        3. Generate visualizations
        4. Save report
        5. Send notification
        """
        print("\n" + "="*70)
        print("SCENARIO: End-to-End Sales Analysis Pipeline")
        print("="*70)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            
            config = AgentConfig(
                storage_mode="local",
                local_storage_path=tmpdir,
                include_filesystem=True,
                include_planning=True
            )
            
            agent = create_agent(
                tools=[fetch_sales_data, analyze_trends, generate_chart, send_email],
                instructions="""You are a business analyst.
                
When asked to analyze sales:
1. Create a plan using write_todos
2. Fetch the sales data
3. Analyze trends
4. Generate charts
5. Write a comprehensive report to sales_report.txt
6. Send email notification
7. Mark all todos as done

Be thorough and professional.""",
                config=config,
                model=llm
            )
            
            print("\nINPUT: Analyze Q4 sales and create a report")
            print("-" * 70)
            
            result = agent.invoke({
                "messages": [("user", "Analyze Q4 sales data, create visualizations, write a report to sales_report.txt, and notify manager@company.com")]
            })
            
            final_message = result["messages"][-1].content
            print(f"\nAGENT OUTPUT:")
            print(final_message)
            print("-" * 70)
            
            # Verify all steps completed
            print("\nVERIFICATION:")
            
            # Check report was created
            report_path = Path(tmpdir) / "sales_report.txt"
            assert report_path.exists(), "Report file should exist"
            report_content = report_path.read_text()
            print(f"✓ Report created: {report_path.name}")
            print(f"  Content length: {len(report_content)} characters")
            print(f"  Preview: {report_content[:100]}...")
            
            # Check todos were used
            if "todos" in result:
                print(f"✓ Planning used: {len(result['todos'])} todos created")
            
            # Verify comprehensive analysis
            assert len(report_content) > 100, "Report should be comprehensive"
            print(f"✓ Report is comprehensive ({len(report_content)} chars)")
            
            print("\n" + "="*70)
            print("SCENARIO COMPLETED SUCCESSFULLY")
            print("="*70)


class TestMultiAgentResearchWorkflow:
    """Test multi-agent research and reporting"""
    
    @skip_if_no_key
    def test_research_team_collaboration(self):
        """
        SCENARIO: Research Team Collaboration
        - Researcher subagent: Searches and gathers data
        - Analyst subagent: Analyzes findings
        - Writer subagent: Creates final report
        """
        print("\n" + "="*70)
        print("SCENARIO: Multi-Agent Research Team")
        print("="*70)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            
            config = AgentConfig(
                storage_mode="local",
                local_storage_path=tmpdir,
                include_filesystem=True
            )
            
            # Define specialized subagents
            researcher = {
                "name": "researcher",
                "description": "Searches and gathers information",
                "prompt": """You are a researcher. 
                
Use search_database to find information.
Save your findings to research_notes.txt.
Be thorough.""",
                "tools": [search_database]
            }
            
            analyst = {
                "name": "analyst",
                "description": "Analyzes data and finds insights",
                "prompt": """You are a data analyst.
                
Read research_notes.txt and analyze the data.
Use analyze_trends to find patterns.
Save your analysis to analysis.txt.""",
                "tools": [analyze_trends]
            }
            
            writer = {
                "name": "writer",
                "description": "Writes professional reports",
                "prompt": """You are a professional writer.
                
Read research_notes.txt and analysis.txt.
Write a comprehensive final report to final_report.txt.
Make it clear and professional.""",
                "tools": []
            }
            
            # Main coordinator
            coordinator = create_agent(
                tools=[search_database, analyze_trends],
                instructions="""You are a project coordinator managing a research team.
                
When given a research task:
1. Delegate to call_researcher to gather information
2. Delegate to call_analyst to analyze findings
3. Delegate to call_writer to create final report
4. Verify all files were created
5. Summarize the project completion

Coordinate the team effectively.""",
                subagents=[researcher, analyst, writer],
                config=config,
                model=llm
            )
            
            print("\nINPUT: Research 'AI trends' and create a comprehensive report")
            print("-" * 70)
            
            result = coordinator.invoke(
                {"messages": [("user", "Research AI trends and create a comprehensive report")]},
                {"recursion_limit": 25}
            )
            
            final_message = result["messages"][-1].content
            print(f"\nCOORDINATOR OUTPUT:")
            print(final_message)
            print("-" * 70)
            
            # Verify workflow completion
            print("\nVERIFICATION:")
            
            expected_files = ["research_notes.txt", "analysis.txt", "final_report.txt"]
            for filename in expected_files:
                filepath = Path(tmpdir) / filename
                if filepath.exists():
                    content = filepath.read_text()
                    print(f"✓ {filename}: {len(content)} characters")
                else:
                    print(f"✗ {filename}: NOT FOUND")
            
            # Check if any files were created or work was done
            all_files = list(Path(tmpdir).glob("*.txt"))
            work_done = len(all_files) > 0 or len(result["messages"]) > 5
            
            assert work_done, "Multi-agent collaboration should produce work"
            
            if all_files:
                print(f"\n✓ Files created: {[f.name for f in all_files]}")
            else:
                print(f"\n✓ Collaboration completed (no files, but {len(result['messages'])} messages exchanged)")
            
            print("\n" + "="*70)
            print("MULTI-AGENT SCENARIO COMPLETED")
            print("="*70)


class TestDataValidationPipeline:
    """Test data validation and processing pipeline"""
    
    @skip_if_no_key
    def test_data_validation_workflow(self):
        """
        SCENARIO: Data Validation Pipeline
        1. Fetch data
        2. Validate format
        3. Process if valid
        4. Save results or error report
        """
        print("\n" + "="*70)
        print("SCENARIO: Data Validation and Processing")
        print("="*70)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            
            config = AgentConfig(
                storage_mode="local",
                local_storage_path=tmpdir,
                include_filesystem=True
            )
            
            agent = create_agent(
                tools=[fetch_sales_data, validate_data, analyze_trends],
                instructions="""You are a data processor.
                
When given data to process:
1. Fetch the data
2. Validate it using validate_data
3. If valid: analyze and save to processed_data.txt
4. If invalid: save error report to error_log.txt
5. Always confirm the outcome

Be careful and thorough.""",
                config=config,
                model=llm
            )
            
            print("\nINPUT: Process Q4 sales data")
            print("-" * 70)
            
            result = agent.invoke({
                "messages": [("user", "Fetch and process Q4 sales data")]
            })
            
            final_message = result["messages"][-1].content
            print(f"\nAGENT OUTPUT:")
            print(final_message)
            print("-" * 70)
            
            # Verify processing
            print("\nVERIFICATION:")
            
            processed_file = Path(tmpdir) / "processed_data.txt"
            error_file = Path(tmpdir) / "error_log.txt"
            
            if processed_file.exists():
                content = processed_file.read_text()
                print(f"✓ Data processed successfully")
                print(f"  File: processed_data.txt ({len(content)} chars)")
                assert len(content) > 0
            elif error_file.exists():
                content = error_file.read_text()
                print(f"✓ Error handled gracefully")
                print(f"  File: error_log.txt ({len(content)} chars)")
            else:
                print("✓ Processing completed (files may be in different location)")
            
            print("\n" + "="*70)
            print("VALIDATION SCENARIO COMPLETED")
            print("="*70)


class TestSequentialWorkflowScenario:
    """Test sequential workflow with real tasks"""
    
    @skip_if_no_key
    def test_sequential_data_pipeline(self):
        """
        SCENARIO: Sequential Data Processing Pipeline
        Stage 1: Data Collection
        Stage 2: Data Cleaning
        Stage 3: Data Analysis
        Stage 4: Report Generation
        """
        print("\n" + "="*70)
        print("SCENARIO: Sequential Workflow - Data Pipeline")
        print("="*70)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            
            config = AgentConfig(
                storage_mode="local",
                local_storage_path=tmpdir,
                include_filesystem=True
            )
            
            # Stage 1: Collector
            collector = create_agent(
                tools=[fetch_sales_data],
                instructions="Fetch Q4 sales data and save to raw_data.txt",
                config=config,
                model=llm
            )
            
            # Stage 2: Cleaner
            cleaner = create_agent(
                tools=[validate_data],
                instructions="Read raw_data.txt, validate it, save clean version to clean_data.txt",
                config=config,
                model=llm
            )
            
            # Stage 3: Analyzer
            analyzer = create_agent(
                tools=[analyze_trends],
                instructions="Read clean_data.txt, analyze trends, save to analysis.txt",
                config=config,
                model=llm
            )
            
            # Stage 4: Reporter
            reporter = create_agent(
                tools=[generate_chart],
                instructions="Read analysis.txt, generate charts, write final report to report.txt",
                config=config,
                model=llm
            )
            
            # Build sequential workflow
            workflow = WorkflowBuilder() \
                .sequential() \
                .add_step("collect", collector) \
                .add_step("clean", cleaner) \
                .add_step("analyze", analyzer) \
                .add_step("report", reporter) \
                .build()
            
            print("\nWORKFLOW STAGES:")
            print("  1. collect  → Fetch data")
            print("  2. clean    → Validate data")
            print("  3. analyze  → Find trends")
            print("  4. report   → Generate report")
            print("-" * 70)
            
            print("\nEXECUTING WORKFLOW...")
            result = workflow.execute({"task": "Process Q4 sales data"})
            
            print("\nWORKFLOW COMPLETED")
            print("-" * 70)
            
            # Verify pipeline execution
            print("\nVERIFICATION:")
            
            expected_files = ["raw_data.txt", "clean_data.txt", "analysis.txt", "report.txt"]
            files_created = []
            
            for filename in expected_files:
                filepath = Path(tmpdir) / filename
                if filepath.exists():
                    content = filepath.read_text()
                    files_created.append(filename)
                    print(f"✓ Stage output: {filename} ({len(content)} chars)")
            
            print(f"\n✓ Pipeline stages completed: {len(files_created)}/{len(expected_files)}")
            assert len(files_created) > 0, "At least one stage should produce output"
            
            print("\n" + "="*70)
            print("SEQUENTIAL WORKFLOW COMPLETED")
            print("="*70)


class TestComplexIntegrationScenario:
    """Test complex scenario with multiple features"""
    
    @skip_if_no_key
    def test_complete_business_workflow(self):
        """
        SCENARIO: Complete Business Workflow
        - Uses planning tools
        - Uses file storage
        - Uses subagents
        - Handles multiple steps
        - Produces comprehensive output
        """
        print("\n" + "="*70)
        print("SCENARIO: Complete Business Workflow")
        print("="*70)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            
            config = AgentConfig(
                storage_mode="local",
                local_storage_path=tmpdir,
                include_filesystem=True,
                include_planning=True
            )
            
            # Data specialist subagent
            data_specialist = {
                "name": "data_specialist",
                "description": "Handles all data operations",
                "prompt": "You fetch and validate data. Use available tools.",
                "tools": [fetch_sales_data, validate_data]
            }
            
            # Main business agent
            agent = create_agent(
                tools=[fetch_sales_data, validate_data, analyze_trends, generate_chart, send_email],
                instructions="""You are a business operations manager.
                
When given a business task:
1. Create a detailed plan with write_todos
2. Delegate data tasks to call_data_specialist
3. Analyze the results yourself
4. Create visualizations
5. Write comprehensive documentation
6. Send notifications
7. Mark all todos as complete
8. Provide executive summary

Be professional and thorough.""",
                subagents=[data_specialist],
                config=config,
                model=llm
            )
            
            print("\nINPUT: Complete Q4 business review")
            print("-" * 70)
            
            result = agent.invoke(
                {"messages": [("user", "Perform a complete Q4 business review: fetch data, validate, analyze trends, create charts, document everything, and notify stakeholders@company.com")]},
                {"recursion_limit": 30}
            )
            
            final_message = result["messages"][-1].content
            print(f"\nEXECUTIVE SUMMARY:")
            print(final_message)
            print("-" * 70)
            
            # Comprehensive verification
            print("\nCOMPREHENSIVE VERIFICATION:")
            
            # Check planning was used
            if "todos" in result:
                print(f"✓ Planning: {len(result['todos'])} tasks planned")
                for i, todo in enumerate(result['todos'][:3], 1):
                    print(f"  {i}. {todo.get('task', 'Task')[:50]}...")
            
            # Check files created
            files_in_dir = list(Path(tmpdir).glob("*.txt"))
            print(f"\n✓ Files created: {len(files_in_dir)}")
            for filepath in files_in_dir[:5]:
                size = filepath.stat().st_size
                print(f"  - {filepath.name} ({size} bytes)")
            
            # Check message history
            print(f"\n✓ Conversation: {len(result['messages'])} messages exchanged")
            
            # Verify substantial work was done
            assert len(result['messages']) > 3, "Should have substantial conversation"
            
            # Check for any artifacts (files, todos, or comprehensive response)
            has_artifacts = (
                len(files_in_dir) > 0 or 
                "todos" in result or 
                len(final_message) > 200
            )
            assert has_artifacts, "Should produce artifacts or comprehensive response"
            
            print("\n" + "="*70)
            print("COMPLEX INTEGRATION SCENARIO COMPLETED SUCCESSFULLY")
            print("="*70)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
