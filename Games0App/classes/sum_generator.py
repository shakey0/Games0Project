import random


class SumGenerator:


    def generate_numbers_and_ops(self, difficulty):
        while True:
            if difficulty == "easy":
                low, high = 1, 9
                ops = ["+", "-"]
                target_number = random.randint(10, 99)
            elif difficulty == "hard":
                low, high = 2, 19
                ops = ["+", "-", "*", "÷"]
                target_number = random.randint(50, 499)
            else: # difficulty == "medium"
                low, high = 3, 9
                ops = ["+", "-", "*", "÷"]
                target_number = random.randint(25, 249)
            
            numbers = [random.randint(low, high) for _ in range(4)]
            ops = [random.choice(ops) for _ in range(2)]

            if ops[0] == "÷":
                numbers[0] *= 10
                numbers[0] += random.randint(1, 9)
                if numbers[0] % numbers[1] != 0:
                    continue
            if ops[1] == "÷":
                numbers[2] *= 10
                numbers[2] += random.randint(1, 9)
                if numbers[2] % numbers[3] != 0:
                    continue

            return numbers, ops, target_number


    def create_sums_for_question(self, difficulty):

        max_end_no = 20 if difficulty == "easy" else 200 if difficulty == "hard" else 100 # If difficulty is medium

        all_choices = []
        for _ in range(4):

            while True:
                sum_numbers, ops, target_number = self.generate_numbers_and_ops(difficulty)
                for item in all_choices:
                    if target_number == item[1]: # MUST TEST FOR DUPLICATE TARGET NUMBERS
                        continue
                exp_part1 = f"({sum_numbers[0]} {ops[0]} {sum_numbers[1]})".replace("÷", "/")
                exp_part2 = f"({sum_numbers[2]} {ops[1]} {sum_numbers[3]})".replace("÷", "/")
                if difficulty == "easy" or difficulty == "medium":
                    if eval(exp_part1) < 1 or eval(exp_part1) > 99 or eval(exp_part2) < 1 or eval(exp_part2) > 99:
                        continue
                expression = f"({sum_numbers[0]} {ops[0]} {sum_numbers[1]}) {random.choice(['+', '-'])} ({sum_numbers[2]} {ops[1]} {sum_numbers[3]})"

                try:
                    value = eval(expression.replace("÷", "/"))
                except ZeroDivisionError:
                    continue
            
                if type(value) == float:
                    if value.is_integer():
                        value = int(value)
                    else:
                        continue
                if value < 0 or value == target_number:
                    continue
                
                if target_number - max_end_no <= value <= target_number + max_end_no:
                    break
                
            if target_number - value > 0:
                corrected_sum = expression + " + " + str(target_number - value)
            else:
                corrected_sum = expression + " - " + str(value - target_number)

            all_choices.append([corrected_sum, target_number])

        # print('ALL TARGET NUMBERS:\n', [item[1] for item in all_choices])
        selected_target = random.choice(all_choices)
        question = f"Which of the following sums equates to {selected_target[1]}?"
        answer = selected_target[0]
        wrong_answers = [item[0] for item in all_choices if item[0] != answer]
        return [question, answer, wrong_answers]
