import csv


def count_questions_by_category(file_path):
    category_counts = {}
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            category = row['category']
            if category in category_counts:
                category_counts[category] += 1
            else:
                category_counts[category] = 1
    sorted_category_counts = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_category_counts


def check_for_duplicate_questions(file_path):
    questions = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            question = row['question']
            id = row['ID']
            if question in questions:
                print(f'Duplicate question: {id}')
            else:
                questions.append(question)


file_path = 'Games0App/static/quiz_data/trivia_from_apis.csv'
print(count_questions_by_category(file_path))
check_for_duplicate_questions(file_path)