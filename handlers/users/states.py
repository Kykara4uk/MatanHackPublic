from aiogram.dispatcher.filters.state import StatesGroup, State

class NewScreenshot(StatesGroup):
    Test = State()
    Exercise = State()
    Photo = State()
    Confirm = State()
    ChangeTest = State()
    ChangeExercise = State()
    ChangePhoto = State()

class Mailing(StatesGroup):
    Text = State()

class Check(StatesGroup):
    Start = State()
    ChooseScreenshot = State()
    AcceptMoney = State()
    RejectionMoney = State()
    Confirm = State()
    ChangeTest = State()
    ChangeExercise = State()
    ChangePhoto = State()
    Change = State()
    ChangeMore = State()

class WriteToAdmins(StatesGroup):
    Text = State()
    ToUser = State()

class PushAlbom(StatesGroup):
    Test = State()
    Exercise = State()
    Photo = State()
    Confirm = State()


class ChangeFromDB(StatesGroup):

    ChangeTest = State()
    ChangeExercise = State()
    ChangePhoto = State()
    Change = State()
    Delete = State()