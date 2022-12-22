import os
#from datetime import date, timedelta
from flask import render_template, flash, redirect, url_for, current_app, send_from_directory, request, abort, Blueprint, session, request
from flask_login import login_required, current_user
#from sqlalchemy import or_
import sys
from copy import deepcopy
from glob import glob
from time import time
from random import shuffle, seed

import yaml

#from scutwork.components import db

quiz_bp = Blueprint('quiz', __name__)
quizzes = dict()

@quiz_bp.route('/')
@login_required
def quiz_index():
    global quizzes
    if len(quizzes) == 0:
        load_quizzes()
        seed()        
        current_app.logger.debug('Loaded %s quizes', len(quizzes))
    if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
    else:
        if 'quiz_name' in session:
            return redirect(url_for('.answer'))
        return render_template(
                    'quiz/select.html',
                    title="Выбор Теста",
                    quiz_list=quizzes.keys(),
                    nquiz=len(quizzes),
                    email=current_user.username)


def strip_response(resp):
    return resp.strip() if isinstance(resp, str) else resp

def get_answer_entered():
    return request.form.get('answer_python', '')

def load_quizzes():
    global quizzes
    quizzes = dict()
    for yml_file in glob('quizzes/*.yml'):
        with open(yml_file, 'r') as stream:
            quiz_d = yaml.load(stream, yaml.FullLoader)
            quizzes[quiz_d['title']] = quiz_d

    # Process questions and detect errors
    for quiz_name, quiz in quizzes.items():
        for i, question in enumerate(quiz['questions']):
            if isinstance(question['correct'], str):
                quizzes[quiz_name]['questions'][i]['correct'] = \
                    strip_response(question['correct'])
            options = [question['correct']]

            if isinstance(question['correct'], bool):
                options.append(str(not question['correct']))
                if 'distractors' not in question:
                    question['distractors'] = str(not question['correct'])
                question['correct'] = str(question['correct'])
                continue # no need to check for distractors

            if isinstance(question['distractors'], list):
                quizzes[quiz_name]['questions'][i]['distractors'] = [
                    strip_response(distractor) \
                    for distractor in question['distractors']]
                options.extend(question['distractors'])
            else:
                quizzes[quiz_name]['questions'][i]['distractors'] = \
                    strip_response(question['distractors'])
                options.append(question['distractors'])

            if len(set(options)) < len(options):
                print('Duplicate options detected for question "%s"!' \
                      % question['prompt'], file=sys.stderr)


@quiz_bp.route('/process', methods=['GET', 'POST'])
@login_required
def answer():
# This app uses flask session variables to keep track of the current question
# the user is on.
    global quizzes
    if request.method == 'POST' and 'quiz_name' not in session:
        # The user just selected a quiz
        selected_quiz = request.form.get('sel_quiz', '')
        is_final_quiz = quizzes[selected_quiz]['final']
        if is_final_quiz and current_user.finals_score is not None:
            return redirect(url_for('quiz.quiz_index'))
        current_app.logger.debug('Select quiz %s', selected_quiz)
        session['quiz_name'] = selected_quiz
    if 'questions' not in session:
        current_app.logger.debug('Copy questions into session')
        session['questions'] = deepcopy(quizzes[session['quiz_name']]['questions'])
        session['complete'] = False

    if 'quiz_name' not in session:
        return redirect(url_for('quiz.quiz_index'))

    if request.method == "POST":
        entered_answer = get_answer_entered()
        if not entered_answer:
            # Show error if no answer entered
            if 'current_question' in session:
                flash("Чтобы продолжить, выберите ответ", "error")

        else:
            # The user has just answered a question

            curr_answer = request.form['answer_python']

            qstn_i = int(session['current_question'])
            current_app.logger.info('question: "%s"', session['questions'][qstn_i]['prompt'])
            current_app.logger.info('entered_answer: "%s"', entered_answer)

            session['questions'][qstn_i]['answer'] = curr_answer

            # Set the current question to the next number when checked
            session['current_question'] = str(qstn_i+1)

            if int(session["current_question"]) < len(session['questions']):
                # If the question exists in the dictionary, redirect to the question
                redirect(url_for('quiz.answer'))

            else:
                # Else, redirect to the summary template as the quiz is complete
                return redirect(url_for('.end_quiz'))

    if "current_question" not in session:
        # The first time the page is loaded, the current question is not set.
        # This means that the user has not answered a question yet. So, set the
        # current question to question in the session to the first one.
        session["current_question"] = "0"

    elif int(session['current_question']) >= len(session['questions']):
        # If the current question number is not available in the questions
        # dictionary, it means that the user has completed the quiz. So show
        # the summary page.
        return redirect(url_for('.end_quiz'))

    # If the request is a GET request
    qstn_i = int(session['current_question'])
    qstn_dict = session['questions'][qstn_i]
    # If the distractors key is not a list, use the single item
    opt_list = list(qstn_dict['distractors'] \
        if isinstance(qstn_dict['distractors'], list) else \
        [qstn_dict['distractors']])
    opt_list.append(qstn_dict['correct'])
    shuffle(opt_list)
    opt_list = [str(opt) for opt in opt_list]

    old_answer = session['questions'][qstn_i]['answer'] \
        if 'answer' in session['questions'][qstn_i] \
        else None
    if 'answer' in session['questions'][qstn_i]:
        current_app.logger.info('old answer %s type %s',
                        old_answer, type(old_answer))
    current_app.logger.debug('opt list: %s', opt_list)


    return render_template(
        'quiz/quiz.html',
        title="ass",
        num=qstn_i+1,
        ntot=len(session['questions']),
        complete=session['complete'],
        question=qstn_dict['prompt'],
        old_answer=old_answer,
        opt_list=opt_list,
        email=current_user.username,
        quiz_name=session['quiz_name'])


@quiz_bp.route('/reload_quizzes', methods=['GET'])
@login_required
def reload_quizzes():
    load_quizzes()
    return redirect(url_for('quiz.quiz_index'))


@quiz_bp.route('/jumpto', methods=['GET', 'POST'])
@login_required
def jump_to():
    #return redirect(url_for('.quiz_index')) # DISABLED
    if request.method == "POST":
        if get_answer_entered():
            curr_answer = request.form['answer_python']
            qstn_i = int(session['current_question'])
            session['questions'][qstn_i]['answer'] = curr_answer

    target = request.args.get('target', '')
    if target:
        session['current_question'] = str(int(target)-1)

    return redirect(url_for('quiz.answer'))


@quiz_bp.route('/reset', methods=['GET', 'POST'])
def reset():
    session.pop('quiz_name', None)
    session.pop('current_question', None)
    session.pop('questions', None)
    session.pop('complete', None)
    return redirect(url_for('.quiz_index'))


@quiz_bp.route('/back', methods=['GET', 'POST'])
@login_required
def back():
    if request.method == "POST":
        if get_answer_entered():
            curr_answer = request.form['answer_python']
            qstn_i = int(session['current_question'])
            session['questions'][qstn_i]['answer'] = curr_answer

    prev_q = max(int(session["current_question"])-1, 0)
    session["current_question"] = str(prev_q)

    return redirect(url_for('.answer'))


@quiz_bp.route('/end', methods=['GET', 'POST'])
@login_required
def end_quiz():
    global quizzes
    is_final_quiz = quizzes[session['quiz_name']]['final']
    if 'current_question' not in session or \
        'questions' not in session:
        return redirect(url_for('.quiz_index'))

    #submission_id = int(time())
    if not session['complete']:
        session['complete'] = int(time())
    submission_id = session['complete']

    for question in session['questions']:
        question['answer_correct'] = question['answer'] == question['correct']
        current_app.logger.debug(
            'correctness decision: %s (type %s) == %s (type %s) : %s',
            question['answer'], type(question['answer']),
            question['correct'], type(question['correct']),
            question['answer_correct'])

    answer_correct_list = [q['answer_correct'] for q in session['questions']]
    n_total = len(session['questions'])
    n_correct = sum(answer_correct_list)
    n_wrong = n_total - n_correct

    wrong_i = [
        i+1 for i, q in enumerate(session['questions']) \
        if not q['answer_correct']]
    wrong_prompts = [
        q['prompt'] for q in session['questions'] \
        if not q['answer_correct']]
    wrong_answers = [
        q['answer'] for q in session['questions'] \
        if not q['answer_correct']]
    wrong_hints = [
        q['hint'] if 'hint' in q else '' \
        for q in session['questions'] \
        if not q['answer_correct']]
    score = int(100 * float(n_correct) / n_total)
    quiz_pass = score >= current_app.config['QUIZ_PASSING_SCORE']

    data = {
        'username': current_user.username,
        'full_name': current_user.name,
        'quiz_name': session['quiz_name'],
        'is_final_quiz': is_final_quiz,
        'n_wrong': n_wrong,
        'n_correct': n_correct,
        'n_total': n_total,
        'questions': [q for q in session['questions'] if not q['answer_correct']],
        'pass': quiz_pass,
        'passing_score': current_app.config['QUIZ_PASSING_SCORE'],
        'score': score
        }
    if not os.path.isdir(current_app.config['SUBMISSIONS_SAVE_PATH']):
        os.mkdir(current_app.config['SUBMISSIONS_SAVE_PATH'])
    with open(current_app.config['SUBMISSIONS_SAVE_PATH'] + '/%d.yaml'%submission_id, 'w') as yamlout:
        yaml.dump(data, yamlout, default_flow_style=False)
#    if quiz_pass:
#        submission_email(submission_id, session['user_email'])
    print(is_final_quiz)
    if is_final_quiz is True:
        print(current_user.finals_score)
        current_user.set_score(score)
        wrong_prompts = None

    return render_template(
        "quiz/end.html",
        title="sasa",
        submission_id=submission_id,
        wrong_i=wrong_i,
        wrong_prompts=wrong_prompts,
        wrong_answers=wrong_answers,
        wrong_hints=wrong_hints,
        #submit_emails=config.DEVEL_EMAILS,
        email=current_user.username,
        quiz_name=session['quiz_name'],
        score=score,
        passing_score=current_app.config['QUIZ_PASSING_SCORE'],
        quiz_pass=quiz_pass)
