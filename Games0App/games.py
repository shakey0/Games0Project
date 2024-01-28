from Games0App.classes.game_play import GamePlay

games = [

    GamePlay(
        name="Fill in the Blank - Facts",
        intro_message="You will be given 10 facts and need to fill in the blank word for each one. Type your answer for each question.",
        param="fill_blank_facts",
        load_route=['csv', 'facts']
    ),

    GamePlay(
        name="Fill in the Blank - Jokes",
        intro_message="You will be given 10 jokes and need to fill in the blank word for each one. Type your answer for each question.",
        param="fill_blank_jokes",
        load_route=['csv', 'jokes']
    ),

    GamePlay(
        name="Trivia Madness",
        intro_message="You will be given 10 questions from your chosen category. Type your answer for each question.",
        param="trivia_madness_categories",
        load_route=['csv', 'trivia_madness'],
        categories = ["Video Games - HARD", "Film", "Music", "Showbiz - HARD", "History", "Geography",
                    "World & Culture - HARD", "General - HARD", "Sports", "Sports & Leisure - HARD",
                    "Science & Nature", "Science - HARD", "Art & Literature - HARD",
                    "Anime & Cartoons - HARD"]
    ),

    GamePlay(
        name="Trivia Madness",
        intro_message="You will be given 10 questions. Type your answer for each question.",
        param="trivia_madness",
        load_route=['csv', 'trivia_madness'],
        default=False # Because there are no categories, and the one with categories is the default
    ),

    GamePlay(
        name="Trivia - Multiple Choice",
        intro_message="You will be given 10 multiple choice questions from your chosen category. Select your answer for each question.",
        param="trivia_mc_categories",
        load_route=['api', 'https://the-trivia-api.com/api/questions?limit=50&categories={}&difficulty={}'],
        categories=["Music", "Sport & Leisure", "Film & TV", "Arts & Literature", "History",
                "Society & Culture", "Science", "Geography", "Food & Drink", "General Knowledge"],
        has_difficulty=True
    ),

    GamePlay(
        name="Trivia - Multiple Choice",
        intro_message="You will be given 10 multiple choice questions. Select your answer for each question.",
        param="trivia_mc",
        load_route=['api', 'https://the-trivia-api.com/api/questions?limit=50&difficulty={}'],
        default=False, # Because there are no categories, and the one with categories is the default
        has_difficulty=True
    ),

    GamePlay(
        name="Trivia - True or False",
        intro_message="You will be given 10 true or false questions from your chosen category. Select True or False for each question.",
        param="trivia_tf_categories",
        load_route=['csv', 'true_or_false_trivia'],
        categories=["Animals", "Countries", "Cities", "Food"]
    ),

    GamePlay(
        name="Trivia - True or False",
        intro_message="You will be given 10 true or false questions. Select True or False for each question.",
        param="trivia_tf",
        load_route=['csv', 'true_or_false_trivia'],
        default=False # Because there are no categories, and the one with categories is the default
    ),

    GamePlay(
        name="Number to Reach",
        intro_message="You will be given 10 questions each with 4 sums. Select the sum that equals the number given.",
        param="number_to_reach_mc",
        load_route=['function', 'sum_generator'],
        has_difficulty=True
    )

]
