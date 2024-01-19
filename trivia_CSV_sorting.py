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
    sorted_category_counts = dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True))
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


category_transfer = {
    "video_games": "video_games",
    "music": "showbiz",
    "film": "showbiz",
    "television": "showbiz",
    "celebrities": "showbiz",
    "tv": "showbiz",
    "entertainment": "showbiz",
    "musicals_and_theatres": "showbiz",
    "geography": "world_culture",
    "history": "world_culture",
    "mythology": "world_culture",
    "historyholidays": "world_culture",
    "politics": "world_culture",
    "religionmythology": "world_culture",
    "general": "general",
    "general_knowledge": "general", 
    "fooddrink": "general",
    "comics": "general",
    "board_games": "general",
    "sports": "sports_leisure",
    "sportsleisure": "sports_leisure",
    "science_and_nature": "science",
    "animals": "science",
    "science": "science",
    "sciencenature": "science",
    "computers": "science",
    "mathematics": "science",
    "gadgets": "science",
    "vehicles": "science",
    "books": "art_literature",
    "artliterature": "art_literature",
    "art": "art_literature",
    "japanese_anime_and_manga": "anime_cartoons",
    "cartoon_and_animations": "anime_cartoons"
}

def compile_all_into_trivia_madness():
    questions = []
    with open('Games0App/static/quiz_data/trivia_from_apis.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            category = category_transfer[row['category']]
            question = row['question']
            answer = row['answer']
            questions.append({'category': category, 'question': question, 'answer': answer})
    with open('Games0App/static/quiz_data/trivia_from_chatgpt.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            category = row['category']
            question = row['question']
            answer = row['answer']
            questions.append({'category': category, 'question': question, 'answer': answer})
    questions = sorted(questions, key=lambda x: x['category'])
    with open('Games0App/static/quiz_data/trivia_madness.csv', mode='w', encoding='utf-8') as file:
        count = 1
        for item in questions:
            id = count
            category = item['category']
            question_ = item['question']
            answer = item['answer']
            file.write(f'{id};{category};{question_};{answer}\n')
            count += 1


file_path = 'Games0App/static/quiz_data/trivia_from_apis.csv'
counts = count_questions_by_category(file_path)
video_game_counts = counts['video_games']
showbiz = counts['music'] + counts['film'] + counts['television'] + counts['celebrities'] + counts['tv'] + counts['entertainment'] + counts['musicals_and_theatres']
world_and_culture_counts = counts['geography'] + counts['history'] + counts['mythology'] + counts['historyholidays'] + counts['politics'] + counts['religionmythology']
general_counts = counts['general'] + counts['general_knowledge'] + counts['fooddrink'] + counts['comics'] + counts['board_games']
sports_and_leisure_counts = counts['sports'] + counts['sportsleisure']
science_counts = counts['science_and_nature'] + counts['animals'] + counts['science'] + counts['sciencenature'] + counts['computers'] + counts['mathematics'] + counts['gadgets'] + counts['vehicles']
art_literature_counts = counts['books'] + counts['artliterature'] + counts['art']
anime_cartoon_counts = counts['japanese_anime_and_manga'] + counts['cartoon_and_animations']
print(f'Video games: {video_game_counts}')
print(f'Showbiz: {showbiz}')
print(f'World and culture: {world_and_culture_counts}')
print(f'General: {general_counts}')
print(f'Sports and leisure: {sports_and_leisure_counts}')
print(f'Science: {science_counts}')
print(f'Art and literature: {art_literature_counts}')
print(f'Anime and cartoons: {anime_cartoon_counts}')
check_for_duplicate_questions(file_path)


# compile_all_into_trivia_madness()
