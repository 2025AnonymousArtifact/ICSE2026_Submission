import os
import re
import subprocess

from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)


def validate_uml_with_syntax_check(uml_code):
    jar_path = os.path.join(
        os.path.dirname(__file__),
        'util', 'plantuml', 'plantuml.jar'
    )
    cmd = ['java', '-jar', jar_path, '-syntax']
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = proc.communicate(uml_code)

    errors = []

    # Java launch failures (e.g. wrong path)
    if err:
        for line in err.strip().splitlines():
            errors.append(f"Java/PlantUML launch error: {line}")

    # Parse PlantUML output for errors
    for line in out.splitlines():
        # Typical error lines start with "ERROR", include "Exception", or "SyntaxError"
        if re.match(r'^(ERROR|SyntaxError|Exception)', line, re.IGNORECASE):
            errors.append(line.strip())
        # Optional: capture "line X" patterns
        elif " line " in line and " :" in line:
            errors.append(line.strip())

    # Non-zero exit code but no error text
    if proc.returncode != 0 and not errors:
        errors.append(f"PlantUML exited with return code {proc.returncode} without detailed message")

    if errors:
        return False, errors
    return True, []


def extract_uml_content(text: str) -> str:
    startuml_index = text.find("@startuml")
    if startuml_index != -1:
        enduml_index = text.find("@enduml", startuml_index + len("@startuml"))
        if enduml_index != -1:
            content_start = startuml_index + len("@startuml")
            return text[content_start:enduml_index].strip()

    start_index = text.find("start\n")
    if start_index == -1:
        return text

    content_start = start_index
    end_index = text.find("@enduml", content_start)
    if end_index == -1:
        return text[content_start:].strip()
    else:
        return text[content_start:end_index].strip()


generatePrompt = ChatPromptTemplate.from_messages(
    messages=[
        SystemMessagePromptTemplate.from_template(
            "You are a PlantUML expert. Given a set of requirements and a format‐reconstruction,"
            "you will produce valid PlantUML activity‐diagram code only."
        ),
        HumanMessagePromptTemplate.from_template(
            "{Examples}\n\nInput:\n{Input}\n\n"
            """
            TASK:
            1. Review the above requirements and its related structured format.
            2. Correct any inconsistencies silently.
            3. Generate the PlantUML code for the activity diagram.
            4. Output _only_ the PlantUML code — no commentary, no explanation, no extra text.
            """
            "\n\n"
            "Output:"
        )
    ]
)

regenerate_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are a PlantUML expert. Fix the following errors in the PlantUML code."
    ),
    HumanMessagePromptTemplate.from_template(
        "{Examples}\n\nInput:\n{Input}\n\n"
        """
        Original TASK:
        1. Review the above requirements and its related structured format.
        2. Correct any inconsistencies silently.
        3. Generate the PlantUML code for the activity diagram.
        4. Output _only_ the PlantUML code — no commentary, no explanation, no extra text.
        """
        "\n\n"
        "Former Output:"
        "{uml_code}\n\n"
        "Errors found during validation:\n"
        "{errors}\n\n"
        "Please correct the code and output ONLY the repaired PlantUML code."
    )
])


class GenerateModule:
    def __init__(self, llm):
        self.llm = llm
        self.generate_chain = generatePrompt | llm
        self.retry_chain = regenerate_prompt | llm

    def invoke(self, examples: str, input_data: str) -> str:
        response = self.generate_chain.invoke({
            "Examples": examples,
            "Input": input_data
        })
        uml_code = extract_uml_content(response.content)

        return self.validate_with_retry(examples, input_data, uml_code)

    def validate_with_retry(self, examples, input_data, initial_uml: str) -> str:
        current_uml = initial_uml
        count = 0
        while True:
            current_uml = extract_uml_content(current_uml)
            if count >= 5:
                return current_uml
            flag, errors = validate_uml_with_syntax_check(current_uml)

            if flag:
                return current_uml

            response = self.retry_chain.invoke({
                "Examples": examples,
                "Input": input_data,
                "errors": "\n".join(errors),
                "uml_code": current_uml
            })
            current_uml = response.content
            count += 1
