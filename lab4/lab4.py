from abc import ABC, abstractmethod
import math

from exceptions import (
    TooLongNameError, NotIsAlphaNameError, InvalidAgeError, InvalidSkillValueError
)

# BASE CLASS
class Person:
    def __init__(self, name: str, age: int):
        self._name = name
        self._age = age

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        if len(name) > 16:
            raise TooLongNameError()
        if not name.isalpha():
            raise NotIsAlphaNameError()
        self._name = name

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value: int):
        if value < 0 or value > 120:
            raise InvalidAgeError()
        self._age = value


# ABSTRACT CLASSES
class Techie(Person, ABC):
    def __init__(self, name: str, age: int, intelligence: int):
        super().__init__(name, age)
        self._intelligence = intelligence   # ← добавили приватное поле

    @property
    def intelligence(self):
        return self._intelligence

    @intelligence.setter
    def intelligence(self, value: int):
        if value < 0:
            raise ValueError("Intelligence cannot be negative.")
        self._intelligence = min(value, 10)   # более красиво и безопасно

    @abstractmethod
    def think_critically(self):
        pass   # можно оставить pass, а можно убрать тело вообще


class Humanitarian(Person, ABC):
    def __init__(self, name: str, age: int, empathy_level: int, creativity: int):
        super().__init__(name, age)
        self.empathy_level = empathy_level
        self.creativity = creativity

    @abstractmethod
    def communicate(self):
        pass   # ← убрали тело, т.к. метод абстрактный

    def dream(self):
        self.creativity = min(self.creativity + 1, 10)

    def __str__(self):
        return f"{self.name}, age {self.age}, empathy level {self.empathy_level}, creativity {self.creativity}"

    def __lt__(self, other):
        if not isinstance(other, Humanitarian):
            return NotImplemented
        return (self.empathy_level + self.creativity) < (other.empathy_level + other.creativity)


# TECHIE CLASSES
class Programmer(Techie):
    def __init__(self, name: str, age: int, intelligence: int, skill: float, status: str, github: str):
        super().__init__(name, age, intelligence)
        self.skill = skill
        self.status = status
        self.github = github

    @property
    def skill(self):
        return self._skill

    @skill.setter
    def skill(self, value: float):
        if value < 0 or value > 10:
            raise InvalidSkillValueError()
        self._skill = value

    def think_critically(self):
        self.intelligence += 0.03
        print(f"{self.name} is thinking critically about a programming problem.")

    def commit(self):
        print(f"{self.name} has committed code to GitHub.")


class Engineer(Techie):
    def __init__(self, name: str, age: int, intelligence: int, experience: int, field: str, projects: int):
        super().__init__(name, age, intelligence)
        self.experience = experience
        self.field = field
        self.projects = projects

    def think_critically(self):
        self.intelligence += 0.04
        print(f"{self.name} is thinking critically about an engineering problem.")

    def build(self):
        self.projects += 1
        print(f"{self.name} is building a project in the field of {self.field}.")

    def destroy(self):
        if self.projects > 0:
            self.projects -= 1
            print(f"{self.name} has destroyed a project in the field of {self.field}.")
        else:
            print(f"{self.name} has no projects to destroy.")

    def __len__(self):
        return self.projects


class Mathematician(Techie):
    def __init__(self, name: str, age: int, intelligence: int, research_area: str):
        super().__init__(name, age, intelligence)
        self.research_area = research_area

    def think_critically(self):
        self.intelligence += 0.07
        print(f"{self.name} is thinking critically about a mathematical problem.")

    def publish_paper(self):
        print(f"{self.name} has published a paper in the research area of {self.research_area}.")

    def __add__(self, other):
        if not isinstance(other, Techie):
            return NotImplemented
        return math.log(self.intelligence + other.intelligence + 1) * 5


# HUMANITARIAN CLASSES
class Teacher(Humanitarian):
    def __init__(self, name: str, age: int, empathy_level: int, creativity: int, subject: str):
        super().__init__(name, age, empathy_level, creativity)
        self.subject = subject

    def communicate(self):
        self.empathy_level = min(self.empathy_level + 1, 10)

    def think(self):
        print(f"{self.name} is thinking about how to teach {self.subject} effectively.")

    def attend_exhibition(self):
        print(f"{self.name} is attending an educational exhibition.")


class Psychologist(Humanitarian):
    def __init__(self, name: str, age: int, empathy_level: int, creativity: int, specialty: str):
        super().__init__(name, age, empathy_level, creativity)
        self.specialty = specialty

    def communicate(self):
        self.empathy_level = min(self.empathy_level + 1, 10)

    def think(self):
        print(f"{self.name} is thinking about how to help patients with {self.specialty}.")

    def attend_exhibition(self):
        print(f"{self.name} is attending a psychology exhibition.")


class ArtCritic(Humanitarian):
    def __init__(self, name: str, age: int, empathy_level: int, creativity: int, art_style: str):
        super().__init__(name, age, empathy_level, creativity)
        self.art_style = art_style

    def communicate(self):
        self.empathy_level = min(self.empathy_level + 1, 10)

    def think(self):
        print(f"{self.name} is thinking about how to critique {self.art_style} art.")

    def attend_exhibition(self):
        print(f"{self.name} is attending an art exhibition.")


# MAIN
if __name__ == "__main__":
    people = []
    try:
        p1 = Programmer("Alex", 25, 7, 8.5, "junior", "github.com/alex")
        p2 = Engineer("Bob", 30, 8, 5, "mechanical", 2)
        p3 = Mathematician("Carl", 40, 9, "Algebra")
        h1 = Teacher("Diana", 35, 7, 6, "Math")
        h2 = Psychologist("Eva", 45, 9, 7, "Anxiety")
        h3 = ArtCritic("Frank", 50, 6, 8, "Modern")
        people.extend([p1, p2, p3, h1, h2, h3])
    except Exception as e:
        print(f"Error while creating objects: {e}")

    print("\n--- ACTIONS ---\n")
    for person in people:
        print(f"{person.name}, age {person.age}")
        if isinstance(person, Techie):
            person.think_critically()
        if isinstance(person, Programmer):
            person.commit()
        if isinstance(person, Engineer):
            person.build()
            person.destroy()
        if isinstance(person, Mathematician):
            person.publish_paper()
        if isinstance(person, Humanitarian):
            person.communicate()
            person.dream()
        if hasattr(person, "think"):
            person.think()
        if hasattr(person, "attend_exhibition"):
            person.attend_exhibition()
        print("-" * 40)

    print("\n--- TEST EXCEPTIONS ---\n")
    try:
        bad_person = Programmer("Alex123", 25, 5, 5.0, "junior", "github.com/test")
    except Exception as e:
        print(f"Caught error: {e}")

    try:
        bad_age = Programmer("Mike", 200, 5, 5.0, "junior", "github.com/test")
    except Exception as e:
        print(f"Caught error: {e}")

    try:
        bad_skill = Programmer("John", 25, 5, 15.0, "junior", "github.com/test")
    except Exception as e:
        print(f"Caught error: {e}")