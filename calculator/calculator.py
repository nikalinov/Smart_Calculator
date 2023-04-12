import re
from collections import deque


class CommandException(Exception):
    def __str__(self):
        return "Unknown command"


class ExpressionError(Exception):
    def __str__(self):
        return "Invalid expression"


class IdentifierError(Exception):
    def __str__(self):
        return "Invalid identifier"


class AssignmentError(Exception):
    def __str__(self):
        return "Invalid assignment"


class UnknownVarError(Exception):
    def __str__(self):
        return "Unknown variable"


def is_empty(inp):
    return not len(inp)


def is_command(inp):
    return '/' == inp[0]


def is_variable(inp):
    return inp.replace(' ', '').isalpha()


def is_assignment(inp):
    return "=" in inp


# order of operators' precedence:
# the higher number, the higher precedence
precedence = {'(': 4, ')': 4, '^': 3, '*': 2, '/': 2, '+': 1, '-': 1}


def to_postfix(infix):
    """
    Convert an infix expression to a postfix one.
    The function uses stack for the converting.

    Arguments:
    infix -- list form of the infix (split by characters).
    Return value:
    postfix -- list in the postfix format.
    """
    stack = deque()
    postfix = []
    for el in infix:
        if el.isdigit() or el.isalpha():
            postfix.append(el)
        elif el == '(':
            stack.append(el)
        # if el == ')', append the postfix with popped values
        # from the stack until '(' is faced. Discard the parentheses.
        elif el == ')':
            while stack[-1] != '(':
                postfix.append(stack.pop())
            stack.pop()
        # if the stack is empty, or the peek is left parenthesis, or
        # prec(el) > prec(peek), append the stack with the incoming element.
        elif len(stack) == 0 \
                or stack[-1] == '(' \
                or precedence[el] > precedence[stack[-1]]:
            stack.append(el)
        # if the stack is not empty and prec(el) <= prec(peek), append
        # the postfix with popped stack values until one of that if false.
        else:
            while len(stack) and \
                    precedence[el] <= precedence[stack[-1]]:
                postfix.append(stack.pop())
            stack.append(el)
    # pop all the stack values and append the postfix with them.
    for _ in range(len(stack)):
        postfix.append(stack.pop())
    return postfix


def check_expr(expr):
    """
    Check a calculation expression for correctness:
    parentheses must be paired, no more than 1 '*', '/', '^'
    symbol in a row. Otherwise, raise an exception.
    Arguments:
    expr -- a string expression to be evaluated.
    Return value: None
    """
    if expr.count('(') != expr.count(')'):
        raise ExpressionError
    elif re.search("[*/^]{2,}", expr) is not None:
        raise ExpressionError


def to_array(expr):
    """
    Return array representation of an expression.
    Divide the expression by numbers, variables,
    operands +, -, *, /, and parentheses.

    Arguments:
    expr -- initial expression (string).
    Return value:
    arr -- array, created from expr.
    """
    arr = []
    i = 0
    while i < len(expr):
        if expr[i].isalpha() or expr[i].lstrip('-').isdigit():
            arr.append(expr[i])
            while i < len(expr) - 1 and \
                    (expr[i + 1].isalpha() or expr[i + 1].lstrip('-').isdigit()):
                arr[-1] += expr[i + 1]
                i += 1
        elif expr[i] == '(' or expr[i] == ')' \
                or expr[i] == '*' or expr[i] == '/':
            arr.append(expr[i])
        elif expr[i] == '^':
            arr.append('**')
        elif re.match("[+|-]+", expr[i:]):
            operator = re.match("[+|-]+", expr[i:]).group(0)
            i += len(operator) - 1
            operator = '-' if operator.count('-') % 2 else '+'
            arr.append(operator)
        i += 1
    return arr


class Calculator:
    """
    The Calculator class which works with variables.

    Main capabilities:
    - calculating expressions with numbers and variables using +, -, *, /, ^;
    - assigning a number or the defined variable's value to a variable;
    - printing the defined variable's value.
    """
    def __init__(self):
        """
        The initialiser for the Calculator class.
        """
        self.run = True
        self.variables = {}

    def assign_valid(self, cmd_arr):
        """
        Evaluate the correctness of an assignment command.
        Raise corresponding exception if the format is invalid.

        Arguments:
        cmd_arr -- array of a variable and a value (number/variable)
        Return value: None
        """
        if len(cmd_arr) != 2:
            raise AssignmentError
        identifier, value = cmd_arr
        # check for identifier correctness
        if not identifier.isalpha():
            raise IdentifierError
        if not value.lstrip("-").isdigit():
            # if the value is not digit and
            # not a valid name, raise AssignmentError
            if not value.isalpha():
                raise AssignmentError
            # else check the value's name in dictionary
            if value not in self.variables:
                raise UnknownVarError

    def assign(self, identifier, value):
        """
        Adds a new variable with a value to the 'variables' dictionary.

        Arguments:
        identifier -- the variable's name;
        value -- the value to be assigned, either a number
                 or a variable from the dictionary.
        Return value: None
        """
        if value.lstrip("-").isdigit():
            self.variables[identifier] = value
        else:
            self.variables[identifier] = self.variables[value]

    def execute_cmd(self, cmd):
        """
        Execute the user's command (starts from '/').

        If the command is '/exit', print 'Bye!' and exit the calculator.
        If the command is '/help', print the calculator description.
        If the command is invalid, raise a custom CommandException.

        Arguments:
        cmd -- an initial command (string)
        Return value: None
        """
        if cmd == "/exit":
            print("Bye!")
            self.run = False
        elif cmd == "/help":
            print("A calculator with variables! Available operations:\n"
                  "-typing any variable to see the value,\n"
                  "-entering an operation with (), +, -, /, *,\n"
                  "-using both numbers and available variables\n")
        else:
            raise CommandException

    def calculate_postfix(self, postfix):
        """
        Calculate a postfix expression and return the result.
        The function uses stack for calculation.

        Arguments:
        postfix -- expression in array format.
        Return value:
        calculated result.
        """
        stack = deque()
        for el in postfix:
            if el.lstrip("-").isdigit():
                stack.append(el)
            elif el.isalpha():
                stack.append(self.variables[el])
            else:
                b, a = stack.pop(), stack.pop()
                stack.append(eval(f"{a} {el} {b}"))
        return int(stack.pop())

    def run_calc(self):
        """
        Run the calculator. Take a user's input and analyse the content.

        The input can be:
        - empty -> nothing happens, continue;
        - a number or a variable -> print it and continue;
        - an assignment -> check the format and assign;
        - a command -> if the command exists, execute;
        - a calculation expression -> convert to array,
        convert to postfix, and calculate the postfix.
        Return value: None
        """
        while self.run:
            inp = input()

            if is_empty(inp):
                continue

            elif inp.lstrip('-').isdigit():
                print(inp)

            elif is_variable(inp):
                try:
                    print(self.variables[inp.replace(' ', '')])
                except KeyError:
                    uve = UnknownVarError()
                    print(uve)
                    continue

            elif is_assignment(inp):
                inp = inp.replace("=", " ").split()
                try:
                    # check for input correctness, raise
                    # error if not correct, else assign
                    self.assign_valid(inp)
                    self.assign(*inp)
                except Exception as e:
                    print(e)
                    continue

            elif is_command(inp):
                try:
                    self.execute_cmd(inp)
                except CommandException as ce:
                    print(ce)

            else:
                try:
                    check_expr(inp)
                except ExpressionError as ee:
                    print(ee)
                    continue
                expr = to_array(inp)
                postfix = to_postfix(expr)
                print(self.calculate_postfix(postfix))


def main():
    calc = Calculator()
    calc.run_calc()


if __name__ == "__main__":
    main()
