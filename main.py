import Interpreter

interpreter = Interpreter.Interpreter()

inputStr = ""

print("Welcome to my own interpriter.")

while True:
    print(">>", end=''),
    inputStr = input()
    result = interpreter.input(inputStr)
    if(result == "exit"):
        break
    if(result != ""):
        print(result)

print('Good by, my friend.')

