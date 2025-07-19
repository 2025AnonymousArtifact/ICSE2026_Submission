from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate
)

reconstructPrompt = ChatPromptTemplate.from_messages(
    messages=[
        SystemMessagePromptTemplate.from_template(
            "You are an expert in integrating analysed requirement information into a structured format. "
        ),
        HumanMessagePromptTemplate.from_template(
            "{Examples}\n\nInput:\n{Input}\n\n"
            "Task:"
            """1. Integrate the identified activities and layerwise decomposed relations for above requirements.
               2. Reformat everything into a well‑structured representation that:
                 • Captures all activities (start, end, decision, fork, join, loops…)  
                 • Preserves layerwise and sequential relations  
                 • Keeps wording faithful to the original text
               3. Return only the structured data—no extra commentary.\n\n"""
            "Output:"
        )
    ]
)


class ReconstructModule:
    def __init__(self, llm):
        self.llm = llm
        self.chain = reconstructPrompt | self.llm

    def invoke(self, examples, data):
        response = self.chain.invoke(
            {"Examples": examples, "Input": data},
        )
        return response.content
