from Games0App.game_play import GamePlay

games = [

    GamePlay(
        name="Fill in the Blank - Facts",
        intro_message="You will be given 10 facts and need to fill in the blank word for each one. Type your answer for each question.",
        param="fill_blank_facts",
        api_source="ninjas",
        api_variable="facts"
    ),

    GamePlay(
        name="Fill in the Blank - Jokes",
        intro_message="You will be given 10 jokes and need to fill in the blank word for each one. Type your answer for each question.",
        param="fill_blank_jokes",
        api_source="ninjas",
        api_variable="jokes"
    ),

    GamePlay(
        name="Trivia Madness",
        intro_message="You will be given 10 questions from your chosen category. Type your answer for each question.",
        categories = ["Art & Literature", "Language", "Science & Nature", "General", "Food & Drink", 
                "People & Places", "Geography", "History & Holidays", "Entertainment",
                "Toys & Games", "Music", "Mathematics", "Religion & Mythology", "Sports & Leisure"],
        param="trivia_madness_categories",
        api_source="ninjas",
        api_variable="trivia"
    ),

    GamePlay(
        name="Trivia Madness",
        intro_message="You will be given 10 questions. Type your answer for each question.",
        default=False, # Because there are no categories, and the one with categories is the default
        param="trivia_madness",
        api_source="ninjas",
        api_variable="trivia"
    ),

    GamePlay(
        name="Trivia - Multiple Choice",
        intro_message="You will be given 10 multiple choice questions from your chosen category. Select your answer for each question.",
        categories=["Music", "Sport & Leisure", "Film & TV", "Arts & Literature", "History",
                "Society & Culture", "Science", "Geography", "Food & Drink", "General Knowledge"],
        has_difficulty=True,
        param="trivia_mc_categories",
        api_source="trivia"
    ),

    GamePlay(
        name="Trivia - Multiple Choice",
        intro_message="You will be given 10 multiple choice questions. Select your answer for each question.",
        default=False, # Because there are no categories, and the one with categories is the default
        has_difficulty=True,
        param="trivia_mc",
        api_source="trivia"
    ),

    GamePlay(
        name="Trivia - True or False",
        intro_message="You will be given 10 true or false questions from your chosen category. Select True or False for each question.",
        categories=["Animals", "Countries", "Cities", "Food"],
        param="trivia_tf_categories"
    ),

    GamePlay(
        name="Trivia - True or False",
        intro_message="You will be given 10 true or false questions. Select True or False for each question.",
        default=False, # Because there are no categories, and the one with categories is the default
        param="trivia_tf"
    ),

    GamePlay(
        name="Number to Reach",
        intro_message="You will be given 10 questions each with 4 sums. Select the sum that equals the number given.",
        has_difficulty=True,
        param="number_to_reach_mc"
    )

]
