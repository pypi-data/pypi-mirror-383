# 仿java的hash计算过程
def hash_code(input_list: []):
    if input_list is None:
        return 0
    result = 1
    for element in input_list:
        result = 31 * result + (0 if element is None else hash(element))
    return result
