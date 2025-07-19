import json
from stanfordcorenlp import StanfordCoreNLP
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate
)
from langgraph.graph import StateGraph, END

decomposePrompt = ChatPromptTemplate.from_messages(
    messages=[
        SystemMessagePromptTemplate.from_template(
            "You are one of the top AI requirements engineers and logicians. "
            "Your task is to analyze requirements texts and derive a rough decomposition result for Information Integration. "
            "Follow the reasoning process below carefully:\n\n"
            "1. Identify key activity events in the text and decompose them layer by layer into basic activity relationship structures, "
            "such as **conditions**, **loops**, and **parallel flows**.\n"
            "2. Starting from the first structure found, determine its **scope** and the **number of branches**.\n"
            "3. Use brackets to represent structure levels:\n"
            "   - Use `{{ }}` for structures that are at the same level (no inclusion).\n"
            "   - Use `[ ]` for nested structures (inclusion relationship).\n"
            "4. Within each branch of every structure, analyze the execution relationships between activities.\n"
            "   - If you detect nested basic relationship structures within a branch, represent them as **nested trigger conditions**, "
            "     but **do not decompose them further at this layer**.\n"
            "5. Organize all activities according to their nested logical structure. "
            "Activities at the same nesting depth should be treated as being on the same level.\n\n"
            "Only output the decomposition result for the **current layer**, based on the previous output (see #Previous Output)."
        ),
        HumanMessagePromptTemplate.from_template(
            "{Examples}\n\n#Input:\n{Input}\n\n"
            "Previous Layers Output:\n{FormerOutput}\n"
            "Please output the result for the current Layer – Level {Level}. Provide **only** the result. "
            "**Do not include any explanation.**\n"
        )
    ]
)

verifyPrompt = ChatPromptTemplate.from_messages(
    messages=[
        SystemMessagePromptTemplate.from_template(
            "You are a top-level AI requirements engineer and logician. "
            "Your task is to evaluate whether a given intermediate nested decomposition of activity relationships is logically sound.\n\n"
            "Activity relationship structures include:\n"
            "- **Conditions**\n"
            "- **Loops**\n"
            "- **Parallel flows**\n\n"
            "Structural notation:\n"
            "- Use `{{ }}` to denote structures at the same level (no inclusion).\n"
            "- Use `[ ]` to denote nested structures (inclusion).\n\n"
            "To validate the decomposition, carefully check the following:\n"
            "1. Whether the **number of branches** at the current layer is correct.\n"
            "2. Whether the **execution order** of activities within each branch is accurate.\n"
            "3. Whether **all nested substructures** have been correctly identified and positioned.\n"
            "4. Whether the structure matches the logic implied by the **input text** and the **dependency tree**.\n"
        ),
        HumanMessagePromptTemplate.from_template(
            "{Examples}\n\n#Input Requirements Text:\n{Input}\n\n"
            "#Previous Layers Output:\n{FormerOutput}\n\n"
            "#Current Layer Output:\n{Output}\n\n"
            "#Dependency Tree:\n{Depend}\n\n"
            "If the decomposition in 'Current Layer Output' is fully correct, respond with: **[Valid]**\n"
            "If there are any issues, respond with a **brief explanation** of the problem(s). Do not provide a full rewrite.\n\n"
            "Evaluation:"
        )
    ]
)

def getTree(data):
    depend_tree = ''
    nlp = StanfordCoreNLP('http://localhost', port=9477, timeout=30000)
    props = {
        'annotators': 'tokenize,ssplit,pos,depparse',
        'outputFormat': 'json'
    }
    try:
        ann = nlp.annotate(data, properties=props)
        j = json.loads(ann)
        dependencies = j['sentences'][0]['basicDependencies']
        tokens = j['sentences'][0]['tokens']
        words = [token['word'] + '-' + str(token['index'] - 1) for token in tokens]
        dependencies.sort(key=lambda arc: arc['dependent'])
        relations = [arc['dep'] for arc in dependencies]
        rely_ids = [arc['governor'] for arc in dependencies]
        heads = ['Root' if gid == 0 else words[gid - 1] for gid in rely_ids]
        for i in range(len(words)):
            depend_tree += f"{relations[i]}({words[i]}, {heads[i]})\n"
    except json.JSONDecodeError:
        print("Error: Server response is not valid JSON. Is the CoreNLP server running and reachable?")
    finally:
        nlp.close()
    return depend_tree

class DecomposeModule:
    def __init__(self, llm, max_retry=5, max_level=10):
        self.llm = llm
        self.max_retry = max_retry
        self.max_level = max_level
        self.executor = decomposePrompt | self.llm
        self.verifier = verifyPrompt | self.llm
        self._build_graph()

    def _build_graph(self):
        def dependency_tree_node(state):
            depend_tree = getTree(state['input_data'])
            return {**state, 'depend_tree': depend_tree}

        def decompose_node(state):
            execution = self.executor.invoke(
                {
                    "Examples": state['examples'],
                    "Input": state['input_data'],
                    "FormerOutput": state.get('former_output', '') + state.get('last_check', ''),
                    "Level": state['level']
                }
            ).content
            return {**state, 'execution': execution}

        def verify_node(state):
            verification = self.verifier.invoke(
                {
                    "Examples": state['examples'],
                    "Input": state['input_data'],
                    "FormerOutput": state.get('former_output', ''),
                    "Output": state['execution'],
                    "Depend": state['depend_tree']
                }
            ).content
            former_output = state.get('former_output', '')
            level = state['level']
            count = state.get('count', 0) + 1
            last_check = '\n' + verification

            if "[Valid]" in verification:
                former_output += state['execution'] + '\n'
                level += 1
                count = 1

                if level > self.max_level:
                    return {
                        **state, 
                        'final_result': former_output + f"\n[Terminated: exceed max_level {self.max_level}]", 
                        'done': True
                    }

                if '[' not in state['execution'] and ']' not in state['execution']:
                    return {**state, 'final_result': former_output, 'done': True}

                return {
                    **state,
                    'former_output': former_output,
                    'last_check': '',
                    'level': level,
                    'count': 1,
                    'done': False
                }

            if count >= self.max_retry:
                return {
                    **state,
                    'final_result': former_output + f"\n[Terminated at level {level} after {self.max_retry} retries. Last check: {verification}]",
                    'done': True
                }

            return {
                **state,
                'last_check': last_check,
                'count': count,
                'done': False
            }

        graph = StateGraph(dict)
        graph.add_node("dependency_tree", dependency_tree_node)
        graph.add_node("decompose", decompose_node)
        graph.add_node("verify", verify_node)
        graph.add_edge("dependency_tree", "decompose")
        graph.add_edge("decompose", "verify")
        graph.add_conditional_edges(
            "verify",
            lambda state: END if state.get("done") else "decompose"
        )
        graph.set_entry_point("dependency_tree")
        self.decompose_graph = graph.compile()

    def invoke(self, examples, data):
        recursion_limit = (self.max_level * self.max_retry) + 20
        state = {
            "examples": examples,
            "input_data": data,
            "former_output": '',
            "last_check": '',
            "level": 1,
            "count": 0
        }
        
        result = self.decompose_graph.invoke(
            state, 
            config={"recursion_limit": recursion_limit}
        )
        return result.get('final_result')
    