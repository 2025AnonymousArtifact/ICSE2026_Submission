from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)

prompt = ChatPromptTemplate.from_messages(
    messages=[
        HumanMessagePromptTemplate.from_template(
            "{Examples}\n\nInput:\n{Input}\n\n"
            "Please generate PlantUML code for the activity diagram according to the above requirements.\n\n"
        )
    ]
)


class CoT:
    def __init__(self, llm):
        self.llm = llm
        self.chain = prompt | self.llm
        with open('prompt/cot.txt', 'r', encoding='utf-8') as file:
            self.examples = file.read()

    def invoke(self, data):
        response = self.chain.invoke(
            {"Examples": self.examples, "Input": data},
        )
        return response.content
