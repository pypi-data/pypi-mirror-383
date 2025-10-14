def get_ratio(num1, num2):
    """
    calculates the ratio between two numbers
    Args:
        num1: first number
        num2: second number
    Returns: 
        _: the ratio between the greater and lesser number (lesser/greater)
        state: a variable indicating which number is larger

    Dependencies: 
        None
    """

    if(num1 > num2):
        state = 1
        return ((num2/num1), state)

    elif(num2 > num1):
        state = 2
        return ( (num1/num2), state)

    else:
        return 0