from module.identify import IdentifyModule
from module.extract import DecomposeModule
from module.generate import GenerateModule
from module.construct import ReconstructModule


class AutoBM:
    def __init__(self, llm):
        self.identification = IdentifyModule(llm)
        self.decomposition = DecomposeModule(llm)
        self.reconstruction = ReconstructModule(llm)
        self.generation = GenerateModule(llm)

    def workflow(self, input_data, examples_path):

        # identifier
        print("START: Activity Identification")
        with open(examples_path + 'identify.txt', 'r', encoding='utf-8') as file:
            identify_examples = file.read()
        identify_result = '#Activity Identification\n' + self.identification.invoke(identify_examples, input_data)
        print("END: Activity Identification")

        # extractor
        print("START: Relation Decomposition")
        with open(examples_path + 'decompose.txt', 'r', encoding='utf-8') as file:
            decompose_examples = file.read()
        decompose_input = input_data + '\n\n'
        decompose_result = '#Relation Decomposition\n' + self.decomposition.invoke(decompose_examples, decompose_input)
        print("END: Relation Decomposition")

        # constructor
        print("START: Information Integration")
        with open(examples_path + 'reconstruct.txt', 'r', encoding='utf-8') as file:
            analyze_examples = file.read()
        analyze_input = input_data + '\n\n' + identify_result + '\n\n' + decompose_result + '\n\n'
        analyze_result = '#Information Integration\n' + self.reconstruction.invoke(analyze_examples, analyze_input)
        print("END: Information Integration")

        # generator
        print("START: Generation")
        with open(examples_path + 'generate.txt', 'r', encoding='utf-8') as file:
            generate_examples = file.read()
        generate_input = input_data + '\n\n' + analyze_result + '\n\n'
        generate_result = self.generation.invoke(generate_examples, generate_input)
        print("END: Generation")

        return generate_result
