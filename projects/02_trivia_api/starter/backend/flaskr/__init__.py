import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import db, setup_db, Question, Category, format_object

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response
    
  @app.route('/categories')
  def categories():
    return jsonify({
      'success': True,
      'categories': [ category.type for category in Category.query.all() ]
    })

  @app.route('/questions')
  def questions():
    page = request.args.get('page', 1, type = int)
    start = (page - 1) * 10
    end = start + 10

    question_list = format_object(Question.query.all())
    category_list = [ category['type'] for category in format_object(Category.query.all()) ]
    paginated_question_list = question_list[start:end]

    return jsonify({
      'success': True,
      'questions': paginated_question_list,
      'total_questions': len(question_list),
      'categories': category_list,
      'current_category': ''
    })

  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
    questions = Question.query                                    \
                        .filter(Question.category == category_id) \
                        .all()

    return jsonify({
      'questions': format_object(questions),
      'totalQuestions': len(questions),
      'currentCategory': category_id
    })

  @app.route('/search', methods=['POST'])
  def search_question():
    search_term = request.json['searchTerm']
    questions = Question.query.filter(Question.question                   \
                                              .ilike(f'%{search_term}%')) \
                              .all()

    return jsonify({
      'questions': format_object(questions),
      'totalQuestions': len(questions),
      'currentCategory': ''
    })

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.get(question_id)
      question.delete()
      db.session.commit()
    except Exception as e:
      print(e)
      db.session.rollback()
      abort(400)
    finally:
      db.session.close()
    
    return jsonify({
      'success': True
    })

  @app.route('/questions', methods=['POST'])
  def create_question():
    try:
      new_question = Question(question = request.json['question'],
                              answer = request.json['answer'],
                              difficulty = request.json['difficulty'],
                              category = request.json['category'])

      db.session.add(new_question)
      db.session.commit()
    except:
      db.session.rollback()
      abort(400)
    finally:
      db.session.close()
    
    return jsonify({
      'success': True
    })

  def get_questions_by_category(quiz_category):
    questions = []

    if (quiz_category['type'] == 'click'):
      questions = Question.query.all()
    else:
      questions = Question.query                                               \
                          .filter(Question.category == quiz_category['id'])  \
                          .all() 

    return format_object(questions)

  def select_random_question(questions, previous_questions):
    '''
      Chooses a random question from a given set of questions
      which has not appeared before

      :param questions: list of eligible questions
      :param previous_questions: list of ids of previously used questions
    '''
    chosen_question = None

    while (True):
      if (len(questions) == len(previous_questions)):
        # This means that all questions have
        # already been used, and therefore
        # the game must end.
        break

      question_index = random.randint(0, len(questions) - 1)
      chosen_question = questions[question_index]
      
      if (not chosen_question['id'] in previous_questions):
        break

    return jsonify({
      'question': chosen_question
    })

  @app.route('/quizzes', methods=['POST'])
  def get_quizzes():
    previous_questions = request.json['previous_questions']
    quiz_category = request.json['quiz_category']
    
    questions = get_questions_by_category(quiz_category)

    return jsonify({
      'question': select_random_question(questions, previous_questions)
    })

  @app.errorhandler(400)
  def not_found(error):
    return jsonify({
      'success': False,
      'message': 'Bad request.'
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'message': 'Not found.'
    }), 404

  @app.errorhandler(405)
  def not_found(error):
    return jsonify({
      'success': False,
      'message': 'The used HTTP method is not allowed.'
    }), 405
  
  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
      'success': False,
      'message': 'The request could not be processed.'
    }), 422

  return app

    