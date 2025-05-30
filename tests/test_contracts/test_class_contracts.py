from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple

import pytest
from nested_preconditions_example import Student

import python_ta.contracts
from python_ta.contracts import check_all_contracts


def is_valid_name(name):
    return name.isalpha()


class Person:
    """
    Represent a person.

    Representation Invariants:
    - self.age > 0
    - len(self.name) > 0
    - is_valid_name(self.name)
    """

    age: int
    name: str
    fav_foods: List[str]
    _other: Optional[Person]

    def __init__(self, name, age, fav_food, other: Optional[Person] = None):
        self.name = name
        self.age = age
        self.fav_foods = fav_food
        self._other = other

    def change_name(self, name: str) -> str:
        self.name = name
        return name

    def change_age(self, age: int) -> int:
        """
        Precondition: age < 150
        """
        self.age = age
        return age

    def decrease_and_increase_age(self, age: int) -> int:
        self.age = -10
        self.age = age
        return age

    def decrease_and_increase_others_age(self, other: Person, age: int) -> int:
        """Temporary violates RI for another instance of the same class."""
        other.age = -10
        other.age = age
        return age

    def decrease_others_age(self, other: Person) -> None:
        """Violate the RI of an argument"""
        other.age = -10

    def decrease_attr_others_age(self) -> None:
        """Violate the RI of an instance attribute"""
        self._other.age = -10

    def add_fav_food(self, food):
        self.fav_foods.append(food)

    def return_mouthful_greeting(self, greeting: str) -> str:
        """
        Return a mouthful (over 20 characters) greeting.

        Postcondition: len($return_value) > 20
        """
        return f"{greeting} {self.name}!"


class Child(Person):
    """Represent a child.

    Representation Invariants:
    - self.age < 10
    """

    def change_someones_name(self, other: Person, name: str) -> None:
        """Temporarily violate an RI of an instance of a parent class

        Precondition:
        - len(name) > 0
        """
        other.name = ""  # Violates the length RI of Person.name
        other.name = name  # Resolves the RI violation

    def remove_someones_name(self, other: Person) -> None:
        """Violate an RI of an instance of a parent class"""
        other.name = ""


def change_age(person, new_age):
    person.age = new_age


class Pizza:
    """
    Representation Invariants:
    - len(self.ingredients) > 0
    - 0 \
        < self.radius \
            <= 10
    """

    def __init__(self, radius, ingredients):
        self.radius = radius
        self.ingredients = ingredients

    @classmethod
    def margherita(cls, radius):
        return cls(radius, ["mozzarella", "tomatoes"])

    def area(self):
        return self.circle_area(self.radius)

    @staticmethod
    def circle_area(r):
        """
        Precondition: r > 0
        """
        return r**2 * math.pi


@dataclass
class SetWrapper:
    """A wrapper around a set.

    Representation Invariants:
        - all(x in self.set for x in {1, 2, 3})
    """

    set: Set[int]


@pytest.fixture
def person():
    return Person("David", 31, ["Sushi"])


@pytest.fixture
def person_2(person):
    return Person("Liu", 31, ["Sushi"], person)


@pytest.fixture
def child():
    return Child("JackJack", 1, ["Cookies"])


def test_change_age_invalid_over(person) -> None:
    """
    Change the age to larger than 150. Expect an exception.
    """
    with pytest.raises(AssertionError) as excinfo:
        person.change_age(200)
    msg = str(excinfo.value)
    assert "age < 150" in msg


def test_change_name_valid(person) -> None:
    """
    Change the name using a valid name.
    """
    person.name = "Ignas"
    assert person.name == "Ignas"


def test_change_name_invalid_nonalpha(person) -> None:
    """
    Change name to contain non-alphabet characters. Expect an exception.
    """
    with pytest.raises(AssertionError) as excinfo:
        person.name = "$$"
    msg = str(excinfo.value)
    assert "is_valid_name(self.name)" in msg


def test_change_age_invalid_in_method(person) -> None:
    """
    Call a method that changes age to something invalid but back to something valid.
    Expects normal behavior.
    """
    age = person.decrease_and_increase_age(10)
    assert age == 10


def test_change_age_of_other_invalid_in_method(person, person_2) -> None:
    """
    Call a method that changes age of another instance of the same class to something invalid but
    back to something valid.
    Expects normal behavior.
    """
    age = person.decrease_and_increase_others_age(person_2, 10)
    assert age == 10


def test_change_name_of_parent_invalid_in_method(person, child) -> None:
    """
    Call a method that changes name of an instance of a parent class to something invalid but
    back to something valid.
    Expects normal behavior.
    This will also check that the child type's RIs are not being enforced on the mutated parent instance.
    """
    child.change_someones_name(person, "Davi")
    assert person.name == "Davi"


def test_violate_ri_in_other_instance(person, person_2) -> None:
    """
    Call a method that changes age of another instance of the same class to something invalid.
    Expects the RI to be violated hence an AssertionError to be raised.
    """
    with pytest.raises(AssertionError) as excinfo:
        person.decrease_others_age(person_2)
    msg = str(excinfo.value)
    assert "self.age > 0" in msg


def test_violate_ri_in_attribute_instance(person_2) -> None:
    """
    Call a method that changes age of an instance attribute of the same class to something invalid.
    Expects the RI to be violated hence an AssertionError to be raised.
    """
    with pytest.raises(AssertionError) as excinfo:
        person_2.decrease_attr_others_age()
    msg = str(excinfo.value)
    assert "self.age > 0" in msg


def test_violate_ri_in_parent_instance(person, child) -> None:
    """
    Call a method that changes name of an instance of a parent class to something invalid.
    Expects the RI to be violated hence an AssertionError to be raised.
    """
    with pytest.raises(AssertionError) as excinfo:
        child.remove_someones_name(person)
    msg = str(excinfo.value)
    assert "len(self.name) > 0" in msg


def test_same_method_names(person) -> None:
    """
    Call a method with the same name as an instance method and ensure reprsentation invariants are checked.
    Expects normal behavior.
    """

    with pytest.raises(AssertionError) as excinfo:
        change_age(person, -10)
    msg = str(excinfo.value)
    assert "self.age > 0" in msg


def test_wrong_food_type(person) -> None:
    """Change fav food to an int. Expect an exception."""

    with pytest.raises(AssertionError):
        person.fav_foods = 5


def test_wrong_food_type_instance_method(person) -> None:
    """Violates type annotation within an instance method. Expect exception."""

    with pytest.raises(AssertionError):
        person.add_fav_food(5)


def test_return_mouthful_greeting_valid(person) -> None:
    """Get a mouthful (over 20 chars) greeting"""

    mouthful_greeting = person.return_mouthful_greeting("Top of the morning to you")
    assert len(mouthful_greeting) > 20


def test_return_mouthful_greeting_invalid(person) -> None:
    """Violated postcondition of return_mouthful_greeting"""

    with pytest.raises(AssertionError):
        person.return_mouthful_greeting("Hello")


def test_create_margherita_invalid() -> None:
    """
    Create circle area with invalid r. Also tests multiline conditions.
    Expect an exception.
    """
    with pytest.raises(AssertionError) as excinfo:
        Pizza.margherita(0)
    msg = str(excinfo.value)
    assert (
        "0 \
        < self.radius \
            <= 10"
        in msg
    )


def test_circle_area_valid() -> None:
    """
    Calculate circle area with valid r.
    """
    a = Pizza.circle_area(10)
    assert a == (10**2 * math.pi)


def test_circle_area_invalid() -> None:
    """
    Calculate circle area with invalid r. Expect an exception.
    """
    with pytest.raises(AssertionError) as excinfo:
        Pizza.circle_area(0)
    msg = str(excinfo.value)
    assert "r > 0" in msg


def test_pizza_valid() -> None:
    """
    Test the Pizza representation invariant on a valid instance.
    """
    pizza = Pizza(radius=5, ingredients=["cheese", "pepperoni"])
    assert pizza.radius == 5 and pizza.ingredients == ["cheese", "pepperoni"]


def test_pizza_invalid() -> None:
    """
    Test the Pizza representation invariant on an invalid instance.
    """
    with pytest.raises(AssertionError) as excinfo:
        Pizza(radius=10, ingredients=[])
    msg = str(excinfo.value)
    assert (
        'Pizza representation invariant "len(self.ingredients) > 0" was violated for instance attributes {'
        "radius: 10, "
        "ingredients: []}" == msg
    )


def test_pizza_invalid_disable_contract_checking(disable_contract_checking) -> None:
    """
    Test the Pizza representation invariant on an invalid instance but with ENABLE_CONTRACT_CHECKING = False so
    no error is raised.
    """
    pizza = Pizza(radius=10, ingredients=[])
    assert pizza.radius == 10 and pizza.ingredients == []


def test_set_wrapper_valid() -> None:
    """
    Test the SetWrapper representation invariant on a valid instance.
    """
    my_set = SetWrapper(set={1, 2, 3})
    assert my_set.set == {1, 2, 3}


def test_set_wrapper_invalid() -> None:
    """
    Test the SetWrapper representation invariant on an invalid instance.
    """
    with pytest.raises(AssertionError) as excinfo:
        SetWrapper(set={1, 2, -3})
    msg = str(excinfo.value)
    assert (
        'SetWrapper representation invariant "all(x in self.set for x in {1, 2, 3})" was violated for instance '
        "attributes {"
        "set: {1, 2, -3}}" == msg
    )


class NoInit:
    """A class with no initializer.

    Representation Invariants:
        - abs(1) < 0  # This is always False
    """

    def method(self) -> int:
        """Method to test that representation invariant is checked on method calls."""
        return 1


def test_no_init_setattr() -> None:
    """
    Check that a built-in function (abs) can be called successfully
    from a representation invariant of a class with no __init__ method, when setting an attribute.
    """
    with pytest.raises(AssertionError) as excinfo:
        n = NoInit()
        n.attr = 1

    msg = str(excinfo.value)
    assert "abs(1) < 0" in msg


def test_no_init_method() -> None:
    """
    Check that a built-in function (abs) can be called successfully
    from a representation invariant of a class with no __init__ method, when calling a method.
    """
    with pytest.raises(AssertionError) as excinfo:
        n = NoInit()
        n.method()

    msg = str(excinfo.value)
    assert "abs(1) < 0" in msg


class NoInit2:
    """A class with no initializer.

    Representation Invariants:
        - is_valid_name('123')  # This is always False
    """

    def method(self) -> int:
        """Method to test that representation invariant is checked on method calls."""
        return 1


def test_no_init_setattr2() -> None:
    """
    Check that a user-defined function (is_valid_name) can be called successfully
    from a representation invariant of a class with no __init__ method, when setting an attribute.
    """
    with pytest.raises(AssertionError) as excinfo:
        n = NoInit2()
        n.attr = 1

    msg = str(excinfo.value)
    assert "is_valid_name('123')" in msg


def test_no_init_method2() -> None:
    """
    Check that a user-defined function (is_valid_name) can be called successfully
    from a representation invariant of a class with no __init__ method, when calling a method.
    """
    with pytest.raises(AssertionError) as excinfo:
        n = NoInit2()
        n.method()

    msg = str(excinfo.value)
    assert "is_valid_name('123')" in msg


def setup_module() -> None:
    """Pytest hook for setting up the module"""
    check_all_contracts(__name__, decorate_main=False)


class OverrideLen:
    """A class that overrides its len method."""

    x: int

    def __init__(self) -> None:
        self.x = 1

    def __len__(self) -> int:
        return self.x


def test_override_len_simple() -> None:
    """Test that we can instantiate OverrideLen, which has a custom __len__ implementation."""
    OverrideLen()


class ThemedWidget:
    """
    Representation Invariants:
    - self.theme.lower() in {'dark', 'light'}
    - self.primary_color.isalpha()
    - self.secondary_color.isalpha()
    """

    size: int
    theme: str
    primary_color: str
    secondary_color: str

    def __init__(self, theme: str, color_palette: Tuple[str, str], options: dict = None) -> None:
        if options:
            self.setup_options(options)
        else:
            self.size = 5
        self.apply_theme(theme)
        self.apply_color_palette(color_palette)

    def setup_options(self, options: dict) -> None:
        if "size" in options:
            self.setup_size(options["size"])

    def setup_size(self, size: int) -> None:
        self.size = size

    def apply_theme(self, theme: str) -> None:
        self.theme = theme

    def apply_color_palette(self, color_palette: Tuple[str, str]) -> None:
        self.primary_color, self.secondary_color = color_palette


def test_no_premature_check_from_helper_in_init() -> None:
    """Test that representation invariants and type annotations of a class still being
    initialized are not checked when a helper called directly from the init returns
    """
    dark_widget = ThemedWidget("dark", ("black", "mahogany"))
    assert dark_widget.theme == "dark"
    assert dark_widget.primary_color == "black"
    assert dark_widget.secondary_color == "mahogany"


def test_no_premature_check_from_deep_helper_in_init() -> None:
    """Test that representation invariants and type annotations of a class still being
    initialized are not checked when a helper of any depth from the init returns
    """
    dark_widget = ThemedWidget("dark", ("black", "mahogany"), options={"size": 10})
    assert dark_widget.theme == "dark"
    assert dark_widget.primary_color == "black"
    assert dark_widget.secondary_color == "mahogany"


def test_invariant_with_function_defined_in_module() -> None:
    """Test that a representation invariant violation is detected when the invariant
    contains a call to a function (top-level, not class method) defined by the user.
    This test is based on the code found at ./test_nested_preconditions_example.py
    """
    with pytest.raises(AssertionError) as exception_info:
        Student("Bob", 0, 19)

    assert (
        str(exception_info.value) == "Student representation invariant "
        '"validate_student_number(self.student_number)" '
        "was violated for instance attributes "
        "{name: " + "'Bob'" + ", student_number: 0, age: 19}"
    )


class Course:
    """Represent a course

    Representation Invariants:
     - self.num_students > 0
     - self.validate_code(self.code)
    """

    code: str
    num_students: int

    def __init__(self, code: str, num_students: int):
        self.code = code
        self.num_students = num_students

    def validate_code(self, code) -> bool:
        """Validate the code for this course"""
        return code != ""


def test_method_invariant_no_violation() -> None:
    """
    Test that no infinite recursion occurs when the representation invariants
    calls a method of the class, and there is NOT a violation.
    """
    course = Course("CSC108", 100)
    assert course.code == "CSC108"
    assert course.num_students == 100


def test_method_invariant_violation() -> None:
    """
    Test that no infinite recursion occurs when the representation invariants
    calls a method of the class, and there is a violation,
    Also, test that the correct error is raised.
    """
    with pytest.raises(AssertionError) as exception_info:
        Course("", 100)

    assert (
        str(exception_info.value) == "Course representation invariant "
        '"self.validate_code(self.code)" was violated for instance attributes'
        " {code: '', num_students: 100}"
    )


def test_method_invariant_set_valid() -> None:
    """
    Test that no infinite recursion occurs when directly setting an attribute
    with a valid value used in a representation invariant calls a class method.
    """
    course = Course("CSC108", 100)
    course.code = "CSC209"
    assert course.code == "CSC209"
    assert course.num_students == 100


def test_method_invariant_set_invalid() -> None:
    """
    Test that no infinite recursion occurs when directly setting an attribute
    with an invalid value used in a representation invariant calls a class method.
    Also, test that the correct error is raised.
    """
    course = Course("CSC108", 100)

    with pytest.raises(AssertionError) as exception_info:
        course.code = ""

    assert (
        str(exception_info.value) == "Course representation invariant "
        '"self.validate_code(self.code)" was violated for instance attributes'
        " {code: '', num_students: 100}"
    )


if __name__ == "__main__":
    pytest.main(["test_class_contracts.py"])
