HISTORICAL_START_DATE = "1997-11-01"
LAST_BALL_COUNT_CHANGE_DATE = "2015-10-07"
NEXT_START_DATE = "2025-04-26"
NEXT_WEEKDAY_DRAWING_MAPPING = {
    0: 2,
    2: 3,
    5: 2,
}


# <---------V2---------->
ALT_CHANGE_RANGE = {
    "first_number": [0.65, 0.90],
    "second_number": [0.60, 0.85],
    "third_number": [0.60, 0.85],
    "fourth_number": [0.70, 0.90],
    "fifth_number": [0.675, 0.90]
}
NUMBER_GENERATION_RANGE = {
    "first_number": (1, 10), # %65
    "first_number_alt": (11, 19), # %25
    "first_number_alt_alt": (20, 30), # %10
# >--------------------------------------------------< #
    "second_number": (11, 30), # %60
    "second_number_alt": (31, 47), # %25
    "second_number_alt_alt": (2, 10), # %15
# >--------------------------------------------------< #
    "third_number": (26, 47), # %60
    "third_number_alt": (10, 25), # %25
    "third_number_alt_alt": (48, 60), # %15
# >--------------------------------------------------< #
    "fourth_number": (35, 59), # %70
    "fourth_number_alt": (60, 65), # %20
    "fourth_number_alt_alt": (26, 34), # %10
# >--------------------------------------------------< #
    "fifth_number": (59, 69), # %65
    "fifth_number_alt": (49, 58), # %20
    "fifth_number_alt_alt": (36, 48) # %15
}
# <---------V2---------->
# Our current chances of winning: 1 in 196,815,528
# Overall chance for powerball: 1 in 292,201,338

