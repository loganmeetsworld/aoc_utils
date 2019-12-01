from bs4 import BeautifulSoup
from colorama import Fore, Style
import os
import requests


def fetch(year, day, content_type):
    headers = {"cookie": f"session={os.environ['SESSION_COOKIE']}",}
    if content_type == 'input':
        response = requests.get(f"https://adventofcode.com/{year}/day/{day}/input", headers=headers)
        _handle_error(response.status_code)
        message = response.text.strip()
    elif content_type == 'problem':
        response = requests.get(f"https://adventofcode.com/{year}/day/{day}", headers=headers)
        _handle_error(response.status_code)
        soup = BeautifulSoup(response.text, "html.parser")
        message = '\n\n\n'.join([a.text for a in soup.select('article')])

    return message


def save(path_to_save, year, day, content_type):
    content = fetch(year, day, content_type)
    with open(f"{path_to_save}/{content_type}.txt", "w") as text_file:
        text_file.write(content)
    
    return content


def detect_time():
    c = os.getcwd()

    return [c.split('/')[-2], c.split('/')[-1].split('-')[1]]


def submit(year, day, level, answer):
    print(f"For Day {day}, Part {level}, we are submitting answer: {answer}")

    headers = {"cookie": f"session={os.environ['SESSION_COOKIE']}",}
    data = {
        "level": str(level),
        "answer": str(answer)
    }

    response = requests.post(f"https://adventofcode.com/{year}/day/{day}/answer", headers=headers, data=data)

    soup = BeautifulSoup(response.text, "html.parser")
    message = soup.article.text

    if "That's the right answer" in message:
        print(f"{Fore.GREEN}Correct! ⭐️{Style.RESET_ALL}")
        star_path = os.getcwd()
        with open(f"{star_path}/stars.txt", "w+") as text_file:
            print("Writing '*' to star file...")
            text_file.write('*')
            if level == 2:
                current_dir = os.curdir
                print("Updated problem with part 2:\n\n")
                print(save(current_dir, year, day, 'problem'))
    elif "That's not the right answer" in message:
        print(f"{Fore.RED}Wrong answer! For details:\n{Style.RESET_ALL}")
        print(message)
    elif f"{Fore.YELLOW}You gave an answer too recently\n{Style.RESET_ALL}" in message:
        print("Wait a bit, too recent a answer...")


def test(test_cases, answer):
    passed = True
    for test_case in test_cases:
        submitted_answer = answer(test_case['input'], test_case['level'])
        if str(test_case['output']) == str(submitted_answer):
            print(f"{Fore.GREEN}Test passed for part {test_case['level']}! for input {test_case['output']}{Style.RESET_ALL}")
        else:
            passed = False
            print(f"{Fore.RED}Test failed :( for input {test_case['input']}, you put {submitted_answer}, correct: {test_case['output']}{Style.RESET_ALL}")

    if passed:
        return 'passed'


def fetch_and_save(year=None, day=None, fetch_part_two=False):
    if not year:
        year, day = detect_time()
    current_dir = os.curdir
    if os.path.exists(f'{current_dir}/input.txt'):
        print('Found input already, using saved input...\n')
        with open(f'{current_dir}/input.txt') as file:
            problem_input = file.read()
    else:
        print('Input not found, fetching...\n')
        problem_input = save(current_dir, year, day, 'input')
        print(save(current_dir, year, day, 'problem'))

    if fetch_part_two:
        print("Attempting to pull part 2, so overwriting previous...")
        print(save(current_dir, year, day, 'problem'))
    
    return problem_input


def check_stars():
    star_path = os.getcwd()
    star_file = f"{star_path}/stars.txt"
    if os.path.exists(star_file):
        with open(star_file, 'r') as file:
            stars = file.read().strip()
            return len(stars)


def test_and_submit(test_cases, problem_input, answer, year=None, day=None):
    if not year:
        year, day = detect_time()

    test_results = test(test_cases, answer)

    if test_results == 'passed':
        print("\nCongratulations! All tests passed.")
        stars = check_stars()
        if stars and stars < 2:
            print('Would you like to submit this answer? y/n')
        else:
            print("It seems we've been here before and you've submitted both answers! ⭐️⭐️")

        if stars == 0:
            part_one_answer = answer(problem_input, 1)
            print(f'Are you sure you want to submit part 1? Answer: {part_one_answer}')
            submit_answer = input()
            if submit_answer == 'y':
                submit(year, day, 1, part_one_answer)

        elif stars == 1:
            part_two_answer = answer(problem_input, 2)
            print(f'Are you sure you want to submit part 2? Answer: {part_two_answer}')
            submit_answer = input()
            if submit_answer == 'y':
                submit(year, day, 2, part_two_answer)


def _handle_error(code):
    if code == 404:
        raise ValueError(f"{Fore.RED}This day is not available yet!{Style.RESET_ALL}")
    elif code == 400:
        raise ValueError(f"{Fore.RED}Bad credentials!{Style.RESET_ALL}")
