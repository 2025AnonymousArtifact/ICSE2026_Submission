from langchain_openai import ChatOpenAI
import yaml


def setup(model, file_path):
    with open(file_path, 'r') as file:
        args = yaml.safe_load(file)[model]
    llm = ChatOpenAI(
        temperature=args['temperature'],
        model=args['model'],
        openai_api_key=args['key'],
        openai_api_base=args['base'],
        # extra_body={"enable_thinking": False}
    )
    print(args)

    return llm
