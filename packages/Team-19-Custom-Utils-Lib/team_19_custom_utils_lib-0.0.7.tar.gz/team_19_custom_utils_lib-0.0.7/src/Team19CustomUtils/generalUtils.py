def get_diff(num1, num2):
    """
    calculates the difference between two numbers
    Args:
        num1: first number
        num2: second number
    Returns: 
        _: the difference between the greater and lesser number
        state: a variable indicating which number is larger

    Dependencies: 
        None
    """

    if(num1 > num2):
        state = 1
        return ((num1 - num2), state)

    elif(num2 > num1):
        state = 2
        return ( (num2 - num1), state)

    else:
        return 0