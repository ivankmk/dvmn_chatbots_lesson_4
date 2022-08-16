import glob
import json

ENCODING = 'KOI8-R'


def covert_txt_to_dict(filename, encoding):
    with open(filename, "r", encoding=encoding) as my_file:
        file_contents = my_file.read()
    questions = []
    answers = []
    for block in file_contents.split('\n\n'):
        if 'Ответ:' in block:
            answers.append(block)
        elif 'Вопрос' in block:
            questions.append(block)

    return dict(zip(questions, answers))


def save_dict_as_json(dict):
    with open('questions.json', 'w') as fp:
        json.dump(dict, fp)


if __name__ == "__main__":
    aggregated_dataset = {}
    for filepath in glob.iglob('questions/*.txt'):
        tokenized_file = covert_txt_to_dict(filepath, ENCODING)
        aggregated_dataset.update(tokenized_file)

    save_dict_as_json(aggregated_dataset)
