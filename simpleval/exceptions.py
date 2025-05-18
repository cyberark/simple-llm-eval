class SimplEvalError(Exception):
    pass


class TerminationError(SimplEvalError):
    pass


class NoWorkToDo(SimplEvalError):
    pass
