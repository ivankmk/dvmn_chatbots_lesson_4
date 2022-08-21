import glob
import json
from dotenv import load_dotenv
import os
import random

ENCODING = 'KOI8-R'

load_dotenv()


def covert_txt_to_dict(filename, encoding):
    with open(filename, "r", encoding=encoding) as my_file:
        file_contents = my_file.read()
    questions = []
    answers = []
    for block in file_contents.split('\n\n'):
        if 'Ответ:' in block:
            answers.append(block.replace('Ответ:', ''))
        elif 'Вопрос' in block:
            questions.append(block)

    return dict(zip(questions, answers))


def save_dict_as_json(dict):
    with open(os.getenv('JSON_FILE'), 'w') as fp:
        json.dump(dict, fp)


def question_cleaner(raw_question):
    pass


def generate_json(questions_path_pattern):
    """
    'questions/*.txt'
    """
    aggregated_dataset = {}
    for filepath in glob.iglob(questions_path_pattern):
        tokenized_file = covert_txt_to_dict(filepath, ENCODING)
        aggregated_dataset.update(tokenized_file)

    save_dict_as_json(aggregated_dataset)


def get_random_question():
    with open(os.getenv('JSON_FILE')) as f:
        dictdump = json.loads(f.read())
        question, answer = list(dictdump.items())[random.randint(0, 100)]
        answer_cleaned = answer.replace('Ответ:', '').strip()
        return {'question': question, 'answer': answer_cleaned}


if __name__ == "__main__":
    pass
