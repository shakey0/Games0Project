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


file_path = 'Games0App/static/quiz_data/trivia_from_apis.csv'
counts = count_questions_by_category(file_path)
video_game_counts = counts['video_games']
showbiz = counts['music'] + counts['film'] + counts['television'] + counts['celebrities'] + counts['tv'] + counts['entertainment'] + counts['tv'] + counts['musicals_and_theatres']
world_and_culture_counts = counts['geography'] + counts['history'] + counts['mythology'] + counts['historyholidays'] + counts['politics'] + counts['religionmythology']
general_counts = counts['general'] + counts['general_knowledge'] + counts['fooddrink'] + counts['comics'] + counts['board_games']
sports_counts = counts['sports'] + counts['sportsleisure']
science_nature_counts = counts['science_and_nature'] + counts['animals'] + counts['science'] + counts['sciencenature'] + counts['computers'] + counts['mathematics'] + counts['gadgets'] + counts['vehicles']
art_literature_counts = counts['books'] + counts['artliterature'] + counts['art']
anime_cartoon_counts = counts['japanese_anime_and_manga'] + counts['cartoon_and_animations']
print(f'Video games: {video_game_counts}')
print(f'Showbiz: {showbiz}')
print(f'World and culture: {world_and_culture_counts}')
print(f'General: {general_counts}')
print(f'Sports: {sports_counts}')
print(f'Science and nature: {science_nature_counts}')
print(f'Art and literature: {art_literature_counts}')
print(f'Anime and cartoons: {anime_cartoon_counts}')
check_for_duplicate_questions(file_path)