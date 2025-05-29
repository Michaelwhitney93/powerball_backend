import requests
from flask import Flask, request
from db.engine import init_db, tear_down_db
from controllers.power_ball.populate_v1 import populate_power_ball_drawings
from controllers.cash_4_life.populate_v1 import populate_cash_4_life_drawings
from controllers.power_ball.generate_v1 import generate_power_ball_drawing_v1
from controllers.power_ball.generate_v2 import generate_power_ball_drawing_v2
from controllers.power_ball.generate_v3 import generate_power_ball_drawing_v3
from controllers.power_ball.generate_v4 import generate_power_ball_drawing_v4, generate_power_ball_drawing_overtime_v4
from controllers.cash_4_life.generate_v4 import generate_cash_4_life_drawing_v4, generate_cash_4_life_drawing_overtime_v4
from db.repositories.power_ball_drawings import PowerballRepository
from db.repositories.cash_4_life_drawings import Cash4LifeRepository
from db.repositories.generations import GenerationRespository
from services.fetch_numbers_service.powerball.fetch_numbers import check_numbers, save_generation
from services.generate_numbers_service.generate import generate_number_with_range

app = Flask(__name__)
init_db()


@app.route("/")
def default():
    return "<p>Hello World!</p>"


@app.route("/drawings/powerball")
def get_power_ball_drawings():
    try:
        populate_power_ball_drawings()
        return {}
    except requests.exceptions.RequestException as e:
        return f"Request Failed: {e}", 500


@app.route("/drawings/cash4life")
def get_cash_4_life_drawings():
    try:
        populate_cash_4_life_drawings()
        return {}
    except requests.exceptions.RequestException as e:
        return f"Request Failed: {e}", 500


@app.route("/generate/powerball/overtime/v4")
def generate_powerball_numbers_over_time():
    try:
        drawing_count = int(request.args.get("drawings", "1"))
        return generate_power_ball_drawing_overtime_v4(drawing_count)
    except Exception as e:
        return f"Request Failed: {e}", 500


@app.route("/generate/cash4life/overtime/v4")
def generate_cash_4_life_numbers_over_time():
    try:
        drawing_count = int(request.args.get("drawings", "1"))
        return generate_cash_4_life_drawing_overtime_v4(drawing_count)
    except Exception as e:
        return f"Request Failed: {e}", 500


@app.route("/generate/powerball/random/v1")
def generate_random_drawing_v1():
    try:
        drawing_count = int(request.args.get("drawings", "1"))
        return generate_power_ball_drawing_v1(drawing_count)
    except Exception as e:
        return f"Request Failed: {e}", 500

@app.route("/generate/powerball/random/v2")
def generate_random_drawing_v2():
    try:
        drawing_count = int(request.args.get("drawings", "1"))
        should_save_generation = request.args.get("save_generation", "False") == "True"
        return generate_power_ball_drawing_v2(drawing_count, should_save_generation)
    except Exception as e:
        return f"Request Failed: {e}", 500


@app.route("/generate/powerball/random/v3")
def generate_random_drawing_v3():
    try:
        drawing_count = int(request.args.get("drawings", "1"))
        should_save_generation = request.args.get("save_generation", "False") == "True"
        range_date = request.args.get("start_date", "2015-10-03")
        return generate_power_ball_drawing_v3(drawing_count, should_save_generation, range_date)
    except Exception as e:
        return f"Request Failed: {e}", 500


@app.route("/generate/powerball/random/v4")
def generate_random_powerball_drawing_v4():
    try:
        drawing_count = int(request.args.get("drawings", "1"))
        should_save_generation = request.args.get("save_generation", "False") == "True"
        range_date = request.args.get("start_date", "2015-10-03")
        return generate_power_ball_drawing_v4(drawing_count, should_save_generation, range_date)
    except Exception as e:
        return f"Request Failed: {e}", 500


@app.route("/generate/cash_4_life/random/v4")
def generate_random_cash4life_drawing_v4():
    try:
        drawing_count = int(request.args.get("drawings", "1"))
        range_date = request.args.get("start_date", "2014-06-16")
        return generate_cash_4_life_drawing_v4(drawing_count, range_date)
    except Exception as e:
        return f"Request Failed: {e}", 500


@app.route("/test/generations")
def test_generations():
    all_generations = list(GenerationRespository.get_all())
    successful_generations = []
    for gen in all_generations:
        numbers_exists = check_numbers(
            gen.first_ball, gen.second_ball, gen.third_ball, gen.fourth_ball, gen.fifth_ball, gen.power_ball
        )
        if numbers_exists:
            successful_generations.append(gen)
    
    return successful_generations


@app.route("/test/drawings")
def test_drawings():
    range_date = request.args.get("start_date", "2014-06-16")
    first_number_ranges = list(Cash4LifeRepository.fetch_occurance_by_ball_position("first_ball", range_date))
    second_number_ranges = list(Cash4LifeRepository.fetch_occurance_by_ball_position("second_ball", range_date))
    third_number_ranges = list(Cash4LifeRepository.fetch_occurance_by_ball_position("third_ball", range_date))
    fourth_number_ranges = list(Cash4LifeRepository.fetch_occurance_by_ball_position("fourth_ball", range_date))
    fifth_number_ranges = list(Cash4LifeRepository.fetch_occurance_by_ball_position("fifth_ball", range_date))
    cash_ball_number_ranges = list(Cash4LifeRepository.fetch_occurance_by_ball_position("cash_ball", range_date))
    v3_generations = []
    v3_number_counts = {}
    for i, _ in enumerate(range(0, 2676)):
        if i % 2 == 0:
            for _ in range(0, 10):
                first_number = generate_number_with_range(first_number_ranges)

            for _ in range(0, 10):
                second_number = generate_number_with_range(second_number_ranges)
                while second_number <= first_number:
                    second_number = generate_number_with_range(second_number_ranges)

            for _ in range(0, 10):
                third_number = generate_number_with_range(third_number_ranges)
                while third_number <= second_number:
                    third_number = generate_number_with_range(third_number_ranges)

            for _ in range(0, 10):
                fourth_number = generate_number_with_range(fourth_number_ranges)
                while fourth_number <= third_number:
                    fourth_number = generate_number_with_range(fourth_number_ranges)

            for _ in range(0, 10):
                fifth_number = generate_number_with_range(fifth_number_ranges)
                while fifth_number <= fourth_number:
                    fifth_number = generate_number_with_range(fifth_number_ranges)
        else:
            for _ in range(0, 10):
                fifth_number = generate_number_with_range(fifth_number_ranges)
            
            for _ in range(0, 10):
                fourth_number = generate_number_with_range(fourth_number_ranges)
                while fourth_number >= fifth_number:
                    fourth_number = generate_number_with_range(fourth_number_ranges)

            for _ in range(0, 10):
                third_number = generate_number_with_range(third_number_ranges)
                while third_number >= fourth_number:
                    third_number = generate_number_with_range(third_number_ranges)
            
            for _ in range(0, 10):
                second_number = generate_number_with_range(second_number_ranges)
                while second_number >= third_number:
                    second_number = generate_number_with_range(second_number_ranges)
            
            for _ in range(0, 10):
                first_number = generate_number_with_range(first_number_ranges)
                while first_number >= second_number:
                    first_number = generate_number_with_range(first_number_ranges)

        for _ in range(0, 10):
            cash_ball = generate_number_with_range(cash_ball_number_ranges)

        v3_generations.append([
            first_number, second_number, third_number, fourth_number, fifth_number, cash_ball
        ])

    for gen in v3_generations:
        for num in range(1, 60):
            if num == gen[0] or num == gen[1] or num == gen[2] or num == gen[3] or num == gen[4]:
                if v3_number_counts.get(str(num)):
                    v3_number_counts[str(num)]["count"] += 1
                    v3_number_counts[str(num)]["percentage"] = v3_number_counts[str(num)]["count"] / 2676
                else:
                    v3_number_counts[str(num)] = { "num": num, "count": 1, "percentage": 1 / 2676 }

    return {
         "v3_generations": v3_number_counts
    }


@app.route("/test/cashball/generations")
def test_powerball_generations():
    range_date = request.args.get("start_date", "2014-06-16")
    first_number_ranges = list(Cash4LifeRepository.fetch_occurance_by_ball_position("first_ball", range_date))
    second_number_ranges = list(Cash4LifeRepository.fetch_occurance_by_ball_position("second_ball", range_date))
    third_number_ranges = list(Cash4LifeRepository.fetch_occurance_by_ball_position("third_ball", range_date))
    fourth_number_ranges = list(Cash4LifeRepository.fetch_occurance_by_ball_position("fourth_ball", range_date))
    fifth_number_ranges = list(Cash4LifeRepository.fetch_occurance_by_ball_position("fifth_ball", range_date))
    cash_ball_number_ranges = list(Cash4LifeRepository.fetch_occurance_by_ball_position("cash_ball", range_date))
    for i, _ in enumerate(range(200_000)):
        if i % 2 == 0:
            for _ in range(0, 10):
                first_number = generate_number_with_range(first_number_ranges)

            for _ in range(0, 10):
                second_number = generate_number_with_range(second_number_ranges)
                while second_number <= first_number:
                    second_number = generate_number_with_range(second_number_ranges)

            for _ in range(0, 10):
                third_number = generate_number_with_range(third_number_ranges)
                while third_number <= second_number:
                    third_number = generate_number_with_range(third_number_ranges)

            for _ in range(0, 10):
                fourth_number = generate_number_with_range(fourth_number_ranges)
                while fourth_number <= third_number:
                    fourth_number = generate_number_with_range(fourth_number_ranges)

            for _ in range(0, 10):
                fifth_number = generate_number_with_range(fifth_number_ranges)
                while fifth_number <= fourth_number:
                    fifth_number = generate_number_with_range(fifth_number_ranges)
        else:
            for _ in range(0, 10):
                fifth_number = generate_number_with_range(fifth_number_ranges)
            
            for _ in range(0, 10):
                fourth_number = generate_number_with_range(fourth_number_ranges)
                while fourth_number >= fifth_number:
                    fourth_number = generate_number_with_range(fourth_number_ranges)

            for _ in range(0, 10):
                third_number = generate_number_with_range(third_number_ranges)
                while third_number >= fourth_number:
                    third_number = generate_number_with_range(third_number_ranges)
            
            for _ in range(0, 10):
                second_number = generate_number_with_range(second_number_ranges)
                while second_number >= third_number:
                    second_number = generate_number_with_range(second_number_ranges)
            
            for _ in range(0, 10):
                first_number = generate_number_with_range(first_number_ranges)
                while first_number >= second_number:
                    first_number = generate_number_with_range(first_number_ranges)
        
        for _ in range(0, 10):
            cash_ball = generate_number_with_range(cash_ball_number_ranges)

        save_generation(
            first=first_number,
            second=second_number,
            third=third_number,
            fourth=fourth_number,
            fifth=fifth_number,
            powerball=cash_ball
        )

    return {}


@app.route("/test/powerball/numbers")
def test_powerball_numbers():
    def number_sort(map):
        return map["percent"]

    number_mapping = []
    for num in range(1, 69):
        count, percent = list(PowerballRepository.fetch_occurance_by_number(
            num, 
            '2023-05-27'
        ))[0]
        print(count)
        if count > 0:
            number_mapping.append({ "num": num, "percent": percent, "count": count })
    
    number_mapping.sort(key=number_sort)
    return { "numbers": number_mapping }


@app.route("/test/cash4life/numbers")
def test_cash_4_life_numbers():
    def number_sort(map):
        return map["percent"]

    number_mapping = []
    for num in range(1, 61):
        count, percent = list(Cash4LifeRepository.fetch_occurance_by_number(num, '2025-04-27'))[0]
        if count > 0:
            number_mapping.append({ "num": num, "percent": percent, "count": count })
    
    number_mapping.sort(key=number_sort)
    return { "numbers": number_mapping }



@app.route("/test/random")
def test_random():
    range_date = request.args.get("start_date", "2023-05-27")
    first_number_ranges = list(Cash4LifeRepository.fetch_occurance_by_ball_position("first_ball", range_date))
    second_number_ranges = list(Cash4LifeRepository.fetch_occurance_by_ball_position("second_ball", range_date))
    third_number_ranges = list(Cash4LifeRepository.fetch_occurance_by_ball_position("third_ball", range_date))
    fourth_number_ranges = list(Cash4LifeRepository.fetch_occurance_by_ball_position("fourth_ball", range_date))
    fifth_number_ranges = list(Cash4LifeRepository.fetch_occurance_by_ball_position("fifth_ball", range_date))
    cash_ball_number_ranges = list(Cash4LifeRepository.fetch_occurance_by_ball_position("cash_ball", range_date))
    all_drawings = list(Cash4LifeRepository.get_all_drawings())
    found_v3_drawing = False
    v3_generation_count = 0

    i = 0
    while found_v3_drawing is False:
        if i % 2 == 0:
            for _ in range(0, 10):
                first_number = generate_number_with_range(first_number_ranges)

            for _ in range(0, 10):
                second_number = generate_number_with_range(second_number_ranges)
                while second_number <= first_number:
                    second_number = generate_number_with_range(second_number_ranges)

            for _ in range(0, 10):
                third_number = generate_number_with_range(third_number_ranges)
                while third_number <= second_number:
                    third_number = generate_number_with_range(third_number_ranges)

            for _ in range(0, 10):
                fourth_number = generate_number_with_range(fourth_number_ranges)
                while fourth_number <= third_number:
                    fourth_number = generate_number_with_range(fourth_number_ranges)

            for _ in range(0, 10):
                fifth_number = generate_number_with_range(fifth_number_ranges)
                while fifth_number <= fourth_number:
                    fifth_number = generate_number_with_range(fifth_number_ranges)
        else:
            for _ in range(0, 10):
                fifth_number = generate_number_with_range(fifth_number_ranges)
            
            for _ in range(0, 10):
                fourth_number = generate_number_with_range(fourth_number_ranges)
                while fourth_number >= fifth_number:
                    fourth_number = generate_number_with_range(fourth_number_ranges)

            for _ in range(0, 10):
                third_number = generate_number_with_range(third_number_ranges)
                while third_number >= fourth_number:
                    third_number = generate_number_with_range(third_number_ranges)
            
            for _ in range(0, 10):
                second_number = generate_number_with_range(second_number_ranges)
                while second_number >= third_number:
                    second_number = generate_number_with_range(second_number_ranges)
            
            for _ in range(0, 10):
                first_number = generate_number_with_range(first_number_ranges)
                while first_number >= second_number:
                    first_number = generate_number_with_range(first_number_ranges)

        for _ in range(0, 10):
            cash_ball = generate_number_with_range(cash_ball_number_ranges)

        existing_drawing = None
        # for drawing in all_drawings:
        #     if drawing.first_ball == first_number and \
        #     drawing.second_ball == second_number and \
        #         drawing.third_ball == third_number and \
        #             drawing.fourth_ball == fourth_number and \
        #                 drawing.fifth_ball == fifth_number and \
        #                 drawing.cash_ball == cash_ball:
        #         existing_drawing = drawing

        if first_number == 9 and second_number == 36 and third_number == 44 and fourth_number == 53 and fifth_number == 59 and cash_ball == 3:
            existing_drawing = True

        if existing_drawing:
            found_v3_drawing = True

        v3_generation_count += 1
        if v3_generation_count % 100000 == 0:
            print(v3_generation_count)
        i += 1

    return { 
        "v3_count": v3_generation_count,
    }


@app.teardown_appcontext
def remove_session(exception=None):
    tear_down_db()


if __name__ == "__main__":
    app.run()
