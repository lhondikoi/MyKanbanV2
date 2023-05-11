from .models import User, Board, List, Card
from application.database import db
from application.cache import cache


# Caching Card queries
@cache.memoize(30)
def get_card_by_id(card_id):
    card = Card.query.get(card_id)
    return card


def get_card_user(card_id):
    return Card.query.get(card_id).list.board.user


def get_card_board(card_id):
    return Card.query.get(card_id).list.board

def get_card_list(card_id):
    return Card.query.get(card_id).list


# Caching List queries

def get_list_by_id(list_id):
    lst = List.query.get(list_id)
    return lst


def get_list_user(list_id):
    return List.query.get(list_id).board.user


def get_list_board(list_id):
    return List.query.get(list_id).board




# Caching Board queries
def get_board_by_id(board_id):
    board = Board.query.get(board_id)
    return board


def get_board_user(board_id):
    return Board.query.get(board_id).user

