from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from . import renderer as rend

class LangQuery:
    """
    A class for querying documents using a LangChain model and prompt configuration.

    This class encapsulates the logic for setting up a ChatPromptTemplate,
    JsonOutputParser, and a LangChain Expression Language chain to process
    document queries and extract structured information.
    """
    def __init__(self, llm, sys_prompt = None, examples = None, document = None):
        """
        Initializes the LangQuery object with a language model and optional
        system prompt, examples, and document.

        Args:
            llm: An instance of a LangChain language model.
            sys_prompt (str, optional): The system prompt for the ChatPromptTemplate.
                                         Defaults to a default NER prompt.
            examples (str, optional): Examples for the ChatPromptTemplate,
                                      formatted as a string. Defaults to a default example.
            document (str, optional): The document to be queried. Defaults to None.
        """
        default_sys_prompt = """
        You are an NER machine. You respond to the users search request over a document and return a JSON object of the specified information.
        Return 'None' where the specified information is not present.
        """

        default_example = """
        {'item1': ['result1', 'result2'],
        'item2': ['result3', 'result4'],
        'item3': 'None'}
        """

        self.llm = llm
        self.sys_prompt = sys_prompt if sys_prompt is not None else default_sys_prompt
        self.examples = examples if examples is not None else default_example
        self.document = document
        self.template = ChatPromptTemplate.from_messages([
            ("system", self.sys_prompt),
            ("ai", "{example}"),
            ("human", "{document}"),
            ("human", "{query}")
        ])
        self.json_parser = JsonOutputParser()
        self.llm_chain = self.template | self.llm | self.json_parser

        if self.document is None:
          print("LangQuery object instantiated without document. Load document with `load_document()`.") # Keep this print for informational purposes

    def query_document(self, query):
        """
        Queries the loaded document using the configured LangChain model and prompt.

        Args:
            query (str): The user's request or query about the document.

        Returns:
            dict: A dictionary containing the extracted information based on the query.
                  Returns None if no document is loaded.
        Raises:
            ValueError: If no document has been loaded into the LangQuery object.
        """
        if self.document is None:
          raise ValueError("No document to query. Load document with `load_document()`.")
        else:
          response = self.llm_chain.invoke(
              {
                  "example": self.examples,
                  "document": self.document,
                  "query": query
              }
          )
          return response

    def set_examples(self, examples):
        """
        Sets new examples for the ChatPromptTemplate.

        Args:
            examples (str): The new examples to be used, formatted as a string.
        """
        self.examples = examples
        print(f"New example set to: \n{self.examples}")

    def examples(self):
        """
        Prints the current examples being used by the ChatPromptTemplate.
        """
        print(f"Current examples: \n{self.examples}")

    def load_document(self, document):
        """
        Loads a document into the LangQuery object for querying.

        Args:
            document (str): The document text as a string.
        """
        if self.document is None:
          self.document = document
          print("Document loaded successfully.")
        else:
          self.document = document
          print("Document replaced. Ensure to rerun query.")

    def render(self, response: dict):
        """
        Highlights the entities found in the document based on the LLM's response.

        Args:
            response (dict): The dictionary response from the LLM's query_document method.
        """
        entity_spans = rend.find_entity_spans(self.document, response)
        displacy_data, displacy_options = rend.prepare_displacy_data(self.document, entity_spans)
        highlighted_html = rend.render_displacy_output(displacy_data, displacy_options)
        rend.display(rend.HTML(highlighted_html))