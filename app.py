
# validatorGen
#    validatorGen('Do you like sushi?',['yes', 'no', 'gross'])
# Generates a function...
# A wrapper for input() which validates input, and rerequests
# on bad input parameters. The first argument is the prompt for the
# user, the second argument is a list which contains valid input.
# returns:
#   valid user input or None
def validatorGen(*arg):
    prompt = arg[0]
    arguments = arg[1]
    def input_validator():
        validated = False
        while (validated == False):
            userInput = input(str(prompt) + " ")
            if type(arguments[0]) == str:
                for i in arguments:
                    if userInput == str(i):
                        validated = True
                        return userInput
            elif type(arguments[0]) == int or type(arguments[0]) == float:
                for i in arguments:
                    if float(userInput) == float(i):
                        validated = True
                        return userInput
        return None
    return validator


def confirmator(input_validator):
    verify = 'n';
    while verify[0] == 'n':
        userInput = input_validator()
        verify = input("You entered " + userInput + ". Do you wish to continue (y or n)? ")
