import glob
import json
from dotenv import load_dotenv
import random

ENCODING = 'KOI8-R'


def covert_txt_to_dict(filename, encoding):
    with open(filename, "r", encoding=encoding) as questions_raw:
        file_contents = questions_raw.read()
    questions = []
    answers = []
    for block in file_contents.split('\n\n'):
        if 'Ответ:' in block:
            answers.append(block.replace('Ответ:', ''))
        elif 'Вопрос' in block:
            questions.append(block)

    return dict(zip(questions, answers))


def shorten_answer(raw_question):
    shortened = raw_question.split('(')[0]
    shortened = shortened.split('.')[0]
    return shortened


def generate_json(questions_path_pattern):
    aggregated_dataset = {}
    for filepath in glob.iglob(questions_path_pattern):
        tokenized_file = covert_txt_to_dict(filepath, ENCODING)
        aggregated_dataset.update(tokenized_file)

    with open(aggregated_dataset, 'w') as file_to_save:
        json.dump(dict, file_to_save)


def get_questions(file_with_questions):
    with open(file_with_questions) as f:
        dictdump = json.loads(f.read())
        return list(dictdump.items())


def get_random_question(questions):
    question, answer = questions[random.randint(0, 100)]
    answer_cleaned = answer.replace('Ответ:', '').strip()
    return {'question': question, 'answer': answer_cleaned}


if __name__ == "__main__":
    load_dotenv()
