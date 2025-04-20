import sqlalchemy as sq
import random
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


Base = declarative_base()


class Words_main(Base):
    
    __tablename__ = 'words_main'

    id = sq.Column(sq.Integer, primary_key=True)
    word_EN = sq.Column(sq.VARCHAR(50), nullable=False)
    word_RU = sq.Column(sq.VARCHAR(50), nullable=False)


class Users(Base):

    __tablename__ = 'users'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=False)
    name_user = sq.Column(sq.VARCHAR(100), nullable=False)


class Person_words(Base):

    __tablename__ = 'person_words'

    id = sq.Column(sq.Integer, primary_key=True)
    word_EN = sq.Column(sq.VARCHAR(50), nullable=False)
    word_RU = sq.Column(sq.VARCHAR(50), nullable=False)
    user_ID = sq.Column(sq.Integer, sq.ForeignKey('users.id'), nullable=False)

    users = relationship(Users, backref='person_words')


class ManangerDB:

    def __init__(self, LOGIN_BD, PASSWORD_BD, NAME_BD, HOST, PORT):

        self.DSN = f'postgresql://{LOGIN_BD}:{PASSWORD_BD}@{HOST}:{PORT}/{NAME_BD}'
        self.engine = sq.create_engine(self.DSN)
        self.Session = sessionmaker(bind=self.engine)


    def create_table(self):

        Base.metadata.create_all(self.engine)


    def import_base_words(self):

        base_words = {
            "I": "Я",
            "She": "Она",
            "He": "Он",
            "City": "Город",
            "Street": "Улица",
            "House": "Дом",
            "Human": "Человек",
            "Dog": "Собака",
            "Cat": "Кошка",
            "Car": "Автомобиль"
        }
        session = self.Session()
        q = session.query(Words_main)
        if q.all():
            return
        for EN, RU in base_words.items():
            words = {'word_EN': EN, 'word_RU': RU}
            session.add(Words_main(**words))
            session.commit()
        session.close()


    def export_base_words(self, mode='EN-RU') -> dict:
        
        session = self.Session()
        q = session.query(Words_main)
        if mode == 'EN-RU':
            data = {x.word_EN:x.word_RU for x in q.all()}
        else:
            data = {x.word_RU:x.word_EN for x in q.all()}
        session.close()
        return data


    def add_new_word(self, userID, word_EN, word_RU):

        session = self.Session()
        imp = {'user_ID': userID, 'word_EN': word_EN, 'word_RU': word_RU}
        session.add(Person_words(**imp))
        session.commit()
        session.close()


    def export_new_words(self, userID, mode='EN-RU') -> dict:

        session = self.Session()
        q = session.query(Person_words).filter(Person_words.user_ID == userID)
        if mode == 'EN-RU':
            data = {x.word_EN:x.word_RU for x in q.all()}
        else:
            data = {x.word_RU: x.word_EN for x in q.all()}
        session.close()
        return data


    def add_new_user(self, userID, name_user):
        
        session = self.Session()
        session.add(Users(id=userID, name_user=name_user))
        session.commit()
        session.close()


    def del_new_word(self, userID, word_EN):

        session = self.Session()
        session.query(Person_words).filter(Person_words.user_ID == userID, Person_words.word_EN == word_EN).delete()
        session.commit()
        session.close()


    def search_user(self, userID) -> bool:

        session = self.Session()
        q = session.query(Users).filter(Users.id == userID)
        if q.all():
            return True
        return False


    def search_word(self, userID, word_EN) -> bool:

        session = self.Session()
        q = session.query(Person_words).filter(Person_words.user_ID == userID, Person_words.word_EN == word_EN)
        if q.all():
            return True
        return False


    def get_words_for_game1(self, userID) -> list:

        session = self.Session()
        dict = {}
        dict.update(self.export_base_words('RU-EN'))
        dict.update(self.export_new_words(userID, 'RU-EN'))
        words = list(dict.keys())
        random.shuffle(words)
        goal_word = words[0]
        right_trans = dict[words[0]]
        incorrect_trans = [dict[x] for x in words[1:4]]
        return [goal_word, right_trans, incorrect_trans]


    def get_words_for_game2(self, userID) -> list:

        session = self.Session()
        dict = {}
        dict.update(self.export_base_words('EN-RU'))
        dict.update(self.export_new_words(userID, 'EN-RU'))
        words = list(dict.keys())
        random.shuffle(words)
        goal_word = words[0]
        right_trans = dict[words[0]]
        incorrect_trans = [dict[x] for x in words[1:4]]
        return [goal_word, right_trans, incorrect_trans]
