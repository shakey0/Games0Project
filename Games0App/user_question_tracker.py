from flask_login import current_user
from Games0App.extensions import db, redis_client
from Games0App.models.user import User
from sqlalchemy import update, func, cast
from sqlalchemy.dialects.postgresql import JSONB


class UserQuestionTracker:
    def __init__(self):
        pass

    
    def asort_questions(self, game_string, last_50_question_ids):

        if any(level in game_string for level in ["triviamultiplechoice_easy", "triviamultiplechoice_medium", "triviamultiplechoice_hard"]):
            limit = 50
        elif "triviamultiplechoice" in game_string:
            limit = 20
        else:
            limit = 50

        if len(last_50_question_ids) > limit:

            while len(last_50_question_ids) > limit:
                last_50_question_ids.pop(0)
            
            update_query = update(User).where(User.id == current_user.id).values(
                last_50_questions=func.jsonb_set(
                    User.last_50_questions, 
                    [game_string], 
                    func.cast(last_50_question_ids, JSONB)
                )
            )
            db.session.execute(update_query)
            db.session.commit()
        
        redis_client.rpush((str(current_user.id) + game_string), *last_50_question_ids)
        redis_client.expire((str(current_user.id) + game_string), 3600)

        return last_50_question_ids
            

    def cache_questions(self, game_string):

        redis_client.delete((str(current_user.id) + game_string))

        user = db.session.query(User).filter(User.id == current_user.id).first()

        if user.last_50_questions:
            last_50_question_ids = user.last_50_questions.get(game_string, [])
            if last_50_question_ids:
                last_50_question_ids = self.asort_questions(game_string, last_50_question_ids)
        

    def deposit_question(self, game_string, question_id):

        cached_questions_ids = redis_client.lrange((str(current_user.id) + game_string), 0, -1)
        # print("CACHED QUESTIONS IDS FROM REDIS:", cached_questions_ids)
        if cached_questions_ids and question_id in [id.decode('utf-8') for id in cached_questions_ids if id]:
            print("QUESTION ALREADY CACHED FOR ID:", question_id)
            return False

        new_questions_value = func.coalesce(
                User.last_50_questions[game_string],
                cast('', JSONB)
            ).concat(cast([question_id], JSONB))

        update_query = (
            update(User)
            .where(User.id == current_user.id)
            .values(
                last_50_questions=func.jsonb_set(
                    User.last_50_questions,
                    [game_string], 
                    new_questions_value
                )
            )
        )
        db.session.execute(update_query)
        db.session.commit()

        redis_client.rpush((str(current_user.id) + game_string), question_id)

        return True
            

    def deposit_question_unauthenticated(self, game_string, question_id, token):

        cached_questions_ids = redis_client.lrange((token + "&&&" + game_string), 0, -1)
        # print("CACHED QUESTIONS IDS FROM REDIS:", cached_questions_ids)
        if cached_questions_ids and question_id in cached_questions_ids:
            print("QUESTION ALREADY CACHED FOR ID:", question_id)
            return False
        
        redis_client.rpush((token + "&&&" + game_string), question_id)
        return True


    def deposit_question_bundle(self, game_string, question_bundle):
        pass
