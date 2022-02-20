import csv
import datetime
from typing import List, Dict, Optional

from pdfminer_test import pdf_text_reader, get_text_lines
from pymupdf_test import get_pages
from question import question
import re


def process_pdf_file_extended(file_path: str, page_map=None, skip_pages: int = 0):
    if page_map is None:
        page_map = dict()
    pages = get_pages(file_path)
    if len(page_map.keys()) == 0:
        out_file_name = str(datetime.datetime)
        question_list = list()
        question_line = None
        question_in_progress = False
        fail_count = 0
        option_in_progress = False
        # explanation_in_progress = False
        page_range = range(skip_pages, len(pages.keys()))
        for page_num in page_range:
            page_lines = pages.get(page_num)
            for line in page_lines:
                line = line.strip()
                if line.startswith('Q.'):
                    if question_line is not None:
                        try:
                            curr_ques = prepare_question(question_line, subject="")
                            if curr_ques is not None:
                                question_list.append(curr_ques)
                            else:
                                fail_count = fail_count + 1
                        except:
                            # print('Error occurred for line: ' + question_line)
                            fail_count = fail_count + 1
                        # explanation_in_progress = False
                    question_line = line
                    question_in_progress = True
                elif line.startswith('(1)') or line.startswith('(2)') or line.startswith('(3)') or line.startswith(
                        '(4)'):
                    if question_in_progress is True:
                        update_question_info(curr_ques, question_line)
                        question_in_progress = False
                        question_line = None
                    elif option_in_progress is True:
                        # if already in progress, we are reading option 2,3 or 4
                        # So, store the option_line to curr_ques
                        update_answer_option_info(curr_ques, option_line)
                    # We have already added previous option line to question
                    # reassign option_line to line. Same goes in case of option 1
                    option_line = line
                    option_in_progress = True
                elif line.startswith('Explanation:'):
                    # explanation_in_progress = True
                    question_in_progress = False
                elif question_in_progress:
                    question_line = question_line + " " + line
            print(" Full File read - Failed lines count - " + str(fail_count))
            write_to_csv_file(question_list, out_file_name)
    else:
        for key in page_map.keys():
            subject = key
            start, end = page_map[key]
            page_range = range(start - 1, end)
            question_list = list()
            question_line = None
            question_in_progress = False
            fail_count = 0
            for page_num in page_range:
                page_lines = pages.get(page_num)
                for line in page_lines:
                    line = line.strip()
                    if line.startswith('Q.'):
                        if question_line is not None:
                            try:
                                curr_ques = prepare_question(question_line, subject=subject)
                                if curr_ques is not None:
                                    question_list.append(curr_ques)
                                else:
                                    fail_count = fail_count + 1
                            except:
                                # print('Error occurred for line: ' + question_line)
                                fail_count = fail_count + 1
                            # explanation_in_progress = False
                        question_line = line
                        question_in_progress = True
                    elif line.startswith('Explanation:'):
                        # explanation_in_progress = True
                        question_in_progress = False
                    elif question_in_progress:
                        question_line = question_line + " " + line
            print(subject + " ::: Failed lines count - " + str(fail_count))
            write_to_csv_file(question_list, subject)


def write_to_csv_file(questions_list: List[question], subject):
    filename = subject + '.csv'
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(
            ['Question Number', 'Question', 'Option 1', 'Option 2', 'Option 3', 'Option 4', 'Correct Answer'])
        for ques in questions_list:
            if ques.question_number is not None and ques.question_text is not None and ques.option_1 is not None and ques.option_2 is not None and ques.option_3 is not None and ques.option_4 is not None and ques.correct_answer is not None:
                writer.writerow(
                    [ques.question_number, ques.question_text, ques.option_1, ques.option_2, ques.option_3,
                     ques.option_4,
                     ques.correct_answer])


def extract_questions_and_write_to_file(file_path, page_range, subject):
    question_list = prepare_questions_from_lines(get_text_lines(file_path, page_range), subject)
    write_to_csv_file(question_list, subject)


def process_test_file(file_path: str) -> None:
    physics_questions: list = prepare_questions_from_lines(get_text_lines(file_path, range(2, 8)), 'Physics')
    for que in physics_questions:
        print(que.__str__())
    # extract_questions_and_write_to_file(file_path, range(2, 218), 'Physics')
    # # extract_questions_and_write_to_file(file_path, range(218, 435), 'Chemistry')
    # # extract_questions_and_write_to_file(file_path, range(435, 735), 'Biology')
    # # extract_questions_and_write_to_file(file_path, range(735, 997), 'History')
    # # extract_questions_and_write_to_file(file_path, range(997, 1282), 'Geography')
    # # extract_questions_and_write_to_file(file_path, range(1282, 1416), 'Economics')
    # # extract_questions_and_write_to_file(file_path, range(1416, 1726), 'Indian_Polity')
    # # extract_questions_and_write_to_file(file_path, range(1726, 1750), 'Railway')


def update_question_info(curr_ques: question, line: str):
    ques_line_parts = line.removeprefix('Q.').split(')')
    curr_ques.question_text = ques_line_parts[1].strip()
    curr_ques.question_number = ques_line_parts[0]


def update_answer_option_info(curr_ques: question, line: str):
    (answer_num, answer_option) = re.compile(r'\((.*)\) (.*)').match(line).groups()
    if answer_num == '1':
        curr_ques.option_1 = answer_option
    elif answer_num == '2':
        curr_ques.option_2 = answer_option
    elif answer_num == '3':
        curr_ques.option_3 = answer_option
    elif answer_num == '4':
        curr_ques.option_4 = answer_option


def prepare_question(question_line: str, subject: str) -> Optional[question]:
    try:
        question_line_splits = question_line.split('(1')
        if len(question_line_splits) == 1:
            if question_line.find('( 1') > 0:
                question_line = question_line.replace('( 1', '(1')
            if question_line.find(' 1)') > 0:
                question_line = question_line.replace(' 1)', ' (1)')
            question_line_splits = question_line.split('(1')
        question_text_raw = question_line_splits[0]

        ques_line_parts = question_text_raw.removeprefix('Q.').split(')')
        question_text = ques_line_parts[1].strip()
        question_number = ques_line_parts[0]
        curr_question = question()
        answer_text: str = '(1' + "(1".join(question_line_splits[1:])
        regex_answer_line = r'\([ 1-9]+[\)}]*[ ]*(.*)\([ 1-9]+[\)}]*[ ]*(.*)\([ 1-9]+[\)}]*[ ]*(.*)\([ 1-9]+[\)}]*[ ]*(.*) [ cC][A-Za-z ]*[–-]*[ ]*(.*)'
        # regex_answer_line = r'\([1-9]+[ ]*\)[ ]*(.*)\([1-9]+[ ]*\)[ ]*(.*)\([1-9]+[ ]*\)[ ]*(.*)\([1-9]+[ ]*\)[ ]*(.*) [ cC][A-Za-z ]*[–-]*[ ]*(.*)'
        # regex_answer_line = r'\(.*\)[ ]*(.*)\(.*\)[ ]*(.*)\(.*\)[ ]*(.*)\(.*\)[ ]*(.*)[cC][A-Za-z ]*[–-]*[ ]*(.*)'
        # regex_answer_line = r'\(1\) (.*)\(2\) (.*)\(3\) (.*)\(4\) (.*)Correct[ ]+Answer[ ]+[–-][ ]+(.*)'
        answer_lines = re.compile(regex_answer_line).match(
            answer_text).groups()
        curr_question.populate(question_number, question_text, answer_lines[0], answer_lines[1], answer_lines[2],
                               answer_lines[3], answer_lines[4], subject)
    except:
        print(subject + ' :: Parse failed for question_line: ' + question_line)
        return None
    return curr_question


def prepare_questions_from_lines(page_lines: list, subject: str) -> List[question]:
    question_list = list()
    question_line = None
    question_in_progress = False
    fail_count = 0
    # explanation_in_progress = False
    for line in page_lines:
        line = line.strip()
        if line.startswith('Q.'):
            if question_line is not None:
                try:
                    curr_ques = prepare_question(question_line, subject)
                    question_list.append(curr_ques)
                except:
                    print(subject + ' :: Error occurred for line: ' + question_line)
                    fail_count = fail_count + 1
                # explanation_in_progress = False
            question_line = line
            question_in_progress = True
        elif line.startswith('Explanation:'):
            # explanation_in_progress = True
            question_in_progress = False
        elif question_in_progress:
            question_line = question_line + " " + line
    print(subject + " ::: Failed lines count - " + str(fail_count))
    return question_list


def prepare_questions_from_lines1(page_lines: list, subject: str) -> List[question]:
    question_list = list()
    curr_ques = None
    question_in_progress = False
    option_in_progress = False
    correct_answer_in_progress = False
    question_line = None
    option_line = None
    answer_line = None

    for line in page_lines:
        line = line.strip()
        if line.startswith('Q.'):
            if curr_ques is not None:
                question_list.append(curr_ques)
            curr_ques = question()
            curr_ques.subject = subject
            question_line = line.strip()
            question_in_progress = True
            option_in_progress = False
            correct_answer_in_progress = False
        elif line.startswith('(1)') or line.startswith('(2)') or line.startswith('(3)') or line.startswith('(4)'):
            if question_in_progress is True:
                update_question_info(curr_ques, question_line)
                question_in_progress = False
                question_line = None
            elif option_in_progress is True:
                # if already in progress, we are reading option 2,3 or 4
                # So, store the option_line to curr_ques
                update_answer_option_info(curr_ques, option_line)
            # We have already added previous option line to question
            # reassign option_line to line. Same goes in case of option 1
            option_line = line
            option_in_progress = True
        elif line.startswith('Correct Answer –'):
            if option_in_progress is True:
                update_answer_option_info(curr_ques, option_line)
                option_in_progress = False
                option_line = None
            if correct_answer_in_progress is False:
                correct_answer_in_progress = True
            answer_line = line
        elif line.startswith('Explanation:'):
            if option_in_progress and 'Correct Answer -' in option_line:
                line_split = option_line.split('Correct Answer -')
                update_answer_option_info(curr_ques, line_split[0])
                option_in_progress = False
                option_line = None
                answer_line = line_split[1]
            curr_ques.correct_answer = answer_line.strip().removeprefix('Correct Answer –')
            correct_answer_in_progress = False
            answer_line = None
        else:
            if question_in_progress:
                question_line = question_line + " " + line
            elif option_in_progress:
                option_line = option_line + " " + line
            elif correct_answer_in_progress:
                answer_line = answer_line + " " + line
    return question_list


if __name__ == '__main__':
    source_file = '/home/pavan/Downloads/10,000+ GK MCQs Ebook.pdf'
    # process_test_file(source_file)
    page_ranges_map = dict({'Physics': (2, 218),
                            'Chemistry': (218, 435),
                            'Biology': (435, 735),
                            'History': (735, 997),
                            'Geography': (997, 1282),
                            'Economics': (1282, 1416),
                            'Indian_Polity': (1416, 1726),
                            'Railway': (1726, 1750)})
    process_pdf_file_extended(file_path=source_file, skip_pages=2, page_map=page_ranges_map)
