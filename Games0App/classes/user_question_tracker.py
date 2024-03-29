from flask_login import current_user
from Games0App.extensions import db, redis_client
from Games0App.models.user import User
from sqlalchemy import update, func, cast
from sqlalchemy.dialects.postgresql import JSONB


class UserQuestionTracker:


    def get_question_storage_limit(self, game_string):
        # This is a temporary fix for the fact that the API being used for 'triviamultiplechoice' only has a
        # limited number of questions for each category.
        if any(x in game_string for x in ["triviamultiplechoice_easy", "triviamultiplechoice_medium", "triviamultiplechoice_hard"]):
            limit = 50
        elif "triviamultiplechoice" in game_string:
            limit = 20
        else:
            limit = 50
        return limit


    def store_last_50_questions(self, game_string, last_50_question_ids):

        update_query = update(User).where(User.id == current_user.id).values(
            last_50_questions=func.jsonb_set(
                User.last_50_questions, 
                [game_string], 
                func.cast(last_50_question_ids, JSONB)
            )
        )
        db.session.execute(update_query)
        db.session.commit()


    def cache_questions(self, game_string):

        question_cache_key = str(current_user.id) + "_question_cache_" + game_string

        redis_client.delete(question_cache_key)

        user = db.session.query(User).filter(User.id == current_user.id).first()

        if user.last_50_questions:
            last_50_question_ids = user.last_50_questions.get(game_string, [])

            if last_50_question_ids:
                limit = self.get_question_storage_limit(game_string) # Temporary fix - See above

                if len(last_50_question_ids) > limit:

                    while len(last_50_question_ids) > limit:
                        last_50_question_ids.pop(0)
                    
                    self.store_last_50_questions(game_string, last_50_question_ids)
                
                redis_client.rpush(question_cache_key, *last_50_question_ids)
                redis_client.expire(question_cache_key, 3600)
        

    def deposit_question(self, game_string, question_id):

        question_cache_key = str(current_user.id) + "_question_cache_" + game_string

        cached_questions_ids = redis_client.lrange(question_cache_key, 0, -1)
        if cached_questions_ids and question_id in [id.decode('utf-8') for id in cached_questions_ids if id]:
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

        redis_client.rpush(question_cache_key, question_id)
        if redis_client.ttl(question_cache_key) == -1:
            redis_client.expire(question_cache_key, 3600)

        return True
            

    def deposit_question_unauth(self, game_string, question_id, token):

        question_cache_key = token + "_unauth_question_cache_" + game_string

        cached_questions_ids = redis_client.lrange(question_cache_key, 0, -1)
        if cached_questions_ids and question_id in [id.decode('utf-8') for id in cached_questions_ids if id]:
            return False
        
        redis_client.rpush(question_cache_key, question_id)
        if redis_client.ttl(question_cache_key) == -1:
            redis_client.expire(question_cache_key, 3600)

        return True


    def deposit_question_bundle(self, question_bundle_ids, game_string):
        
        user = db.session.query(User).filter(User.id == current_user.id).first()

        if user.last_50_questions:
            last_50_question_ids = user.last_50_questions.get(game_string, [])

            if last_50_question_ids:

                all_question_ids = last_50_question_ids + question_bundle_ids
                all_question_ids.reverse()
                filtered_question_ids = []
                for id in all_question_ids:
                    if id not in filtered_question_ids:
                        filtered_question_ids.append(id)
                filtered_question_ids.reverse()

                limit = self.get_question_storage_limit(game_string) # Temporary fix - See above
            
                while len(filtered_question_ids) > limit:
                    filtered_question_ids.pop(0)

                self.store_last_50_questions(game_string, filtered_question_ids)
            
            else:
                self.store_last_50_questions(game_string, question_bundle_ids)
        else:
            self.store_last_50_questions(game_string, question_bundle_ids)


user_question_tracker = UserQuestionTracker()
