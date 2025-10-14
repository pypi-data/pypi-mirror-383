def a_reduce_dim(input):
    output = [0] *( len(input) * len(input[0]) )
    k = 0
    for i in range(0, len(input)):
        for j in range(0, len(input[0])):
            output[k] = input[i][j]
            k += 1
    return output