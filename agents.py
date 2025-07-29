import os
from typing import Type
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from linkup import LinkupClient
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool

# Load environment variables (for non-LinkUp settings)
load_dotenv()


def get_client_llm():
    """LLM client initialization"""
    return LLM(
        model = "ollama/deepseek-r1:7b",
        base_url = "http://localhost:11434"
    )


class SearchInput(BaseModel):
    """LinkUp Search Tool Input Schema"""
    # The search query to perform
    query: str = Field(description = "The search query to perform")
    # Depth of search: 'standard' or 'deep'
    depth: str = Field(default = "standard",
                       description = "Depth of search: 'standard' or 'deep'")
    # Output type: 'searchResults', 'sourcedAnswer', or 'structured'
    output_type: str = Field(
        default = "searchResults", description = "Output type: 'searchResults', 'sourcedAnswer', or 'structured'")


class SearchTool(BaseTool):
    """LinkUp Search Tool"""
    name: str = "LinkUp Search"
    description: str = "Search the web for information using LinkUp and return comprehensive results"
    args_schema: Type[BaseModel] = SearchInput

    def __init__(self):
        super().__init__()

    def _run(self, query: str, depth: str = "standard", output_type: str = "searchResults") -> str:
        """LinkUp search execution and response generation."""
        try:
            # Initialize LinkUp client with API key from environment variables
            linkup_client = LinkupClient(api_key=os.getenv("API_KEY"))

            # Perform search
            search_response = linkup_client.search(
                query = query,
                depth = depth,
                output_type = output_type
            )

            return str(search_response)
        except Exception as err:
            return f"Error: {str(err)}"


def create_crew(query: str):
    """Research Crew Creation and Configuration"""
    # Initialize tools
    search_tool = SearchTool()

    # Get LLM client
    client_llm = get_client_llm()

    # Define the web searcher
    web_surfer = Agent(
        role = "Web Searcher",
        goal = "Find the most relevant information on the web, along with source links (urls).",
        backstory = "An expert at formulating search queries and retrieving relevant information. Passes the results to the 'Research Analyst' only.",
        verbose = True,
        allow_delegation = True,
        tools = [search_tool],
        llm = client_llm,
    )

    # Define the research analyst
    researcher = Agent(
        role = "Research Analyst",
        goal = "Analyze and synthesize raw information into structured insights, along with source links (urls) as citations.",
        backstory = "An expert at analyzing information, identifying patterns, and extracting key insights. If required, can delagate the task of fact checking/verification to 'Web Searcher' only. Passes the final results to the 'Technical Writer' only.",
        verbose = True,
        allow_delegation = True,
        llm = client_llm,
    )

    # Define the technical writer
    tech_writer = Agent(
        role = "Technical Writer",
        goal = "Create well-structured, clear, and comprehensive responses in markdown format, with citations/source links (urls).",
        backstory = "An expert at communicating complex information in an accessible way.",
        verbose = True,
        allow_delegation = False,
        llm = client_llm,
    )

    # Define tasks
    searcher = Task(
        description = f"Search for comprehensive information about: {query}.",
        agent = web_surfer,
        expected_output = "Detailed raw search results including sources (urls).",
        tools = [search_tool]
    )

    analyser = Task(
        description = "Analyze the raw search results, identify key information, verify facts and prepare a structured analysis.",
        agent = researcher,
        expected_output = "A structured analysis of the information with verified facts and key insights, along with source links",
        context = [searcher]
    )

    writer = Task(
        description = "Create a comprehensive, well-organized response based on the research analysis.",
        agent = tech_writer,
        expected_output = "A clear, comprehensive response that directly answers the query with proper citations/source links (urls).",
        context = [analyser]
    )

    # Create the crew
    crew = Crew(
        agents = [web_surfer, researcher, tech_writer],
        tasks = [searcher, analyser, writer],
        verbose = True,
        process = Process.sequential
    )

    return crew


def research(query: str):
    """Run the research process and return results"""
    try:
        crew = create_crew(query)
        res = crew.kickoff()
        return res.raw
    except Exception as err:
        return f"Error: {str(err)}"