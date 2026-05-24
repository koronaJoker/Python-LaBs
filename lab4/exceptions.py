class MyError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class TooLongNameError(MyError):
    def __init__(self, message="Name is too long. It should be less than 16 characters."):
        super().__init__(message)

class NotIsAlphaNameError(MyError):
    def __init__(self, message="Name should contain only alphabetic characters."):
        super().__init__(message)

class InvalidAgeError(MyError):
    def __init__(self, message="Age should be between 0 and 120."):
        super().__init__(message)

class InvalidStatusError(MyError):
    def __init__(self, message="Status should be either 'student' or 'professional'."):
        super().__init__(message)

class InvalidSkillValueError(MyError):
    def __init__(self, message="Skill should be between 0 and 10."):
        super().__init__(message)        