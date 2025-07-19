from fastcoref import FCoref
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate
)
from langgraph.graph import StateGraph, END

identifyPrompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are an expert in extracting atomic activities from free‑form requirements text "
        "and representing them for UML activity diagrams."
    ),
    HumanMessagePromptTemplate.from_template(
        "{Examples}\n\n"
        "Input Requirements Text:\n"
        "{Input}\n\n"
        "Instructions:\n"
        "1. Identify **all** atomic activity names discussed in the text.\n"
        "2. Output **only** a JSON array of strings, each string being one activity name.\n"
        "3. Do **not** include any additional commentary, descriptions, or formatting.\n\n"
        "Output:"
    )
])

calibratePrompt = ChatPromptTemplate.from_messages(
    messages=[
        SystemMessagePromptTemplate.from_template(
            "You are an expert in extracting atomic activities from free‑form requirements text "
            "and representing them for UML activity diagrams."
        ),
        HumanMessagePromptTemplate.from_template(
            "{Examples}\n\n"
            "Input Requirements Text:\n"
            "{Input}\n\n"
            "Previous Extraction (Last Output):\n"
            "{Output}\n\n"
            "CoReference Information:\n"
            "{CoreF}\n\n"
            "Instructions:\n"
            "1. Review the **Previous Extraction** list of extracted activity names against the requirements text.\n"
            "2. Use the **CoReference Information** to resolve any pronouns or aliases.\n"
            "3. Determine if any atomic activities are missing, merged incorrectly, or oversimplified.\n"
            "4. If the extraction is complete and correct, output exactly:\n"
            "   [OK]\n"
            "5. Otherwise, output a **revised** JSON array of strings:\n"
            "   [\n"
            "     \"<activity name 1>\",\n"
            "     \"<activity name 2>\",\n"
            "     …\n"
            "   ]\n"
            "6. Do **not** include any additional commentary, descriptions, or formatting.\n\n"
            "Output:"
        )
    ]
)

def get_max_calibrate_rounds(input_data):
    length = len(input_data)
    if length < 200:
        return 3
    elif length < 800:
        return 6
    else:
        return 8

class IdentifyModule:
    def __init__(self, llm):
        self.llm = llm
        self.model = FCoref(device='cuda:0')
        self._build_graph()

    def _build_graph(self):
        def identify_node(state):
            chain = identifyPrompt | self.llm
            res = chain.invoke({"Examples": state['examples'], "Input": state['input_data']})
            new_state = dict(state)
            new_state.update({
                "last_output": res.content
            })
            return new_state

        def coref_node(state):
            coref_result = self.model.predict(texts=[state['input_data']])
            new_state = dict(state)
            new_state.update({
                "coref_result": coref_result
            })
            return new_state

        def calibrate_node(state):
            calibrator = calibratePrompt | self.llm
            count = state.get('calibrate_count', 0) + 1
            prev_output = state.get('prev_output', None)
            res = calibrator.invoke({
                "Examples": state['examples'],
                "Input": state['input_data'],
                "Output": state['last_output'],
                "CoreF": state['coref_result'],
            }).content
            max_rounds = get_max_calibrate_rounds(state['input_data'])
            new_state = dict(state)
            if '[OK]' in res or count >= max_rounds or res == prev_output:
                new_state.update({
                    "final_result": state['last_output'],
                    "calibrate_count": count,
                    "done": True
                })
            else:
                new_state.update({
                    "last_output": res,
                    "calibrate_count": count,
                    "prev_output": state['last_output'],
                    "done": False
                })
            return new_state

        graph = StateGraph(dict)
        graph.add_node("identify", identify_node)
        graph.add_node("coref", coref_node)
        graph.add_node("calibrate", calibrate_node)
        graph.add_edge("identify", "coref")
        graph.add_edge("coref", "calibrate")
        graph.add_conditional_edges(
            "calibrate",
            lambda state: END if state.get("done") else "calibrate"
        )
        graph.set_entry_point("identify")
        self.identify_graph = graph.compile()

    def calibrate(self, examples, input_data, last_output):
        coref_result = self.model.predict(texts=[input_data])
        calibrator = calibratePrompt | self.llm
        count = 0
        result = last_output
        prev_result = None
        max_rounds = get_max_calibrate_rounds(input_data)
        while True:
            count += 1
            res = calibrator.invoke({
                "Examples": examples,
                "Input": input_data,
                "Output": result,
                "CoreF": coref_result,
            }).content
            if '[OK]' in res or count >= max_rounds or res == prev_result:
                return result
            else:
                prev_result = result
                result = res

    def invoke(self, examples, data):
        state = {
            "llm": self.llm,
            "examples": examples,
            "input_data": data,
            "last_output": None,
            "calibrate_count": 0,
            "prev_output": None
        }
        result = self.identify_graph.invoke(state)
        return result.get("final_result")
