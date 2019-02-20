import re
from collections import deque

def tokenize(expression):
    if expression == "":
        return []

    regex = re.compile("\s*(=>|[-+*\/\%=\(\)]|[A-Za-z_][A-Za-z0-9_]*|[0-9]*\.?[0-9]+)\s*")
    tokens = regex.findall(expression)
    return [s for s in tokens if not s.isspace()]

def IsNum(s):
    if type(s) is float or type(s) is int:
        return True

    regex = re.compile("^[0-9]+(\.[0-9]+)?$")
    return regex.match(s)

def IsIdent (s):
    if type(s) is not str:
        return False

    regex = re.compile("^[A-Za-z_][A-Za-z_0-9]*$")
    return regex.match(s)

class Interpreter:
    def __init__(self):
        self.vars = {}
        self.functions = {}

    def GetNum(self, s):
        if type(s) is not str:
            return s

        if(re.match("\.", s)):
            return float(s)

        return int(s)

    def Calculate(self, exprerssion):
        stack = deque()
        exprerssion = deque(exprerssion)

        for s in exprerssion:
            if IsNum(s) or (IsIdent(s) and s not in self.functions.keys()):
                stack.append(s)
                continue

            if s in self.functions.keys():
                if len(stack) < self.functions[s]['varCount']:
                    return "Function '" + s + "' gets more variables."

                parameters = deque()
                for i in range(self.functions[s]['varCount']):
                    parameters.appendleft(stack.pop())

                parameters = list(parameters)
                funcResult = self.CalculateFunc(s, parameters)
                stack.append(funcResult)
                continue

            if(stack.__len__() == 0):
                return None

            rightOp = stack.pop()
            if IsIdent(rightOp):
                if rightOp not in self.vars.keys():
                    return "Identified '" + rightOp + "' not found."

                rightOp = self.vars[rightOp]

            rightOp = self.GetNum(rightOp)
            leftOp = stack.pop()
            if s == '=':
                if not IsIdent(leftOp):
                    return None

                self.vars[leftOp] = rightOp
                stack.append(rightOp)
                continue

            if IsIdent(leftOp):
                if leftOp not in self.vars.keys():
                    return "Identified '" + leftOp + "' not found."
                leftOp = self.vars[leftOp]

            leftOp = self.GetNum(leftOp)

            if s == '+':
                stack.append(leftOp + rightOp)
            elif s == '-':
                stack.append(leftOp - rightOp)
            elif s == '*':
                stack.append(leftOp * rightOp)
            elif s == '/':
                if type(leftOp) is int and type(rightOp) is int:
                    stack.append(int(leftOp / rightOp))
                else:
                    stack.append(leftOp / rightOp)
            elif s == '%':
                stack.append(leftOp % rightOp)

        if len(stack) != 1:
            return None

        result = stack.pop()
        if IsIdent(result):
            if result not in self.vars.keys():
                return "Identified '" + result + "' not found"

            result = self.vars[result]

        return self.GetNum(result)

    def GetOpNum(self, s):
        if s in self.functions.keys():
            return 8
        else:
            return opNum[s]

    def GetPolsk(self, tokens):
        tokens = deque(tokens)
        tokens.append('#')

        result = deque()
        stack = deque('#')

        while True:
            s = tokens.popleft()

            if IsNum(s):
                result.append(s)
                continue

            if IsIdent(s) and s not in self.functions.keys():
                result.append(s)
                continue

            if s in opNum.keys() or s in self.functions.keys():
                lastOp = stack.pop()

                opCode = opTable[self.GetOpNum(lastOp)][self.GetOpNum(s)]

                if opCode == 1:
                    stack.append(lastOp)
                    stack.append(s)

                elif opCode == 2:
                    result.append(lastOp)
                    tokens.appendleft(s)

                elif opCode == 4:
                    return result

                elif opCode == 5:
                    return "Incorrect expression"
            else:
                return "Identified '" + s + "' not found."

    def EnterFun(self, tokens):
        tokens = deque(tokens)

        if len(tokens) < 4:
            return None

        tokens.popleft()
        funcName = tokens.popleft()

        if funcName in self.vars.keys():
            return None

        funcVars = {}
        varsCount = 0

        s = tokens.popleft()
        while s != '=>':
            if s in funcVars.keys():
                return None

            funcVars[s] = '$' + str(varsCount)
            varsCount += 1
            s = tokens.popleft()

        funcBodyPolsk = list(self.GetPolsk(tokens))
        for i in range(len(funcBodyPolsk)):
            s = funcBodyPolsk[i]
            if IsNum(s) or s in opNum.keys():
                continue

            if s not in funcVars.keys():
                return None

            funcBodyPolsk[i] = funcVars[s]

        self.functions[funcName] = {'varCount': varsCount, 'body': funcBodyPolsk}

        return ''

    def CalculateFunc(self, fName, parameters):
        if fName not in self.functions.keys():
            return None

        if len(parameters) != self.functions[fName]['varCount']:
            return None

        regex = re.compile("^\$([0-9]+)$")
        funcBody = list(self.functions[fName]['body'])
        for i in range(len(funcBody)):
            s = funcBody[i]
            if IsNum(s) or s in opNum.keys():
                continue

            s = regex.findall(s)
            funcBody[i] = parameters[int(s[0])]

        return self.Calculate(funcBody)


    def ProcessExperession(self, expression):
        tokens = tokenize(expression)
        if len(tokens) == 0:
            return ""

        if tokens[0] == 'exit':
            return "exit"

        if tokens[0] == 'fn':
            return self.EnterFun(tokens)

        polsk = self.GetPolsk(tokens)
        if type(polsk) is str:
            return polsk
        if polsk is None:
            return None

        return self.Calculate(polsk)

    def input(self, expression):
        result = self.ProcessExperession(expression)

        if result is None:
            return("Invalid expresssion.")

        return result

opTable = [
        [4, 1, 1, 1, 1, 1, 1, 1, 1, 5],
        [2, 1, 1, 1, 1, 1, 1, 1, 1, 2],
        [2, 5, 2, 2, 1, 1, 1, 1, 1, 2],
        [2, 5, 2, 2, 1, 1, 1, 1, 1, 2],
        [2, 5, 2, 2, 2, 2, 2, 1, 1, 2],
        [2, 5, 2, 2, 2, 2, 2, 1, 1, 2],
        [2, 5, 2, 2, 2, 2, 2, 1, 1, 2],
        [5, 1, 1, 1, 1, 1, 1, 1, 1, 3],
        [2, 5, 2, 2, 2, 2, 2, 1, 1, 2]
        ]

opNum = {'#': 0, '=': 1, '+': 2, '-': 3, '*': 4, '%': 5, '/': 6, '(': 7, ')': 9}
