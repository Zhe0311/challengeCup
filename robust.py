def get_potential_errors(filename: str) -> dict:
    """get the list of potential errors"""
    with open(filename) as f:
        for line in f:
            potential_errors = eval(line)
    return potential_errors

def get_common_prefix(label1: str, label2: str) -> str:
    """find the common prefix of the left book and the right book"""
    common_prefix = ""
    for i in range(min(len(label1), len(label2))):
        if label1[i] == label2[i]:
            common_prefix += label1[i]
        else:
            break
    return common_prefix

def error_correct(labels: list, old_error_index: list, prefix_len_th: int) -> list:
    """get rid of the index that maight be right but we think it's wrong"""
    potential_errors = get_potential_errors("potentialErrors.txt")
    new_error_index = []
    for error_index in old_error_index:

        # ignore the first label and last label
        if error_index == 0 or error_index == len(labels)-1:
            new_error_index.append(error_index)
            continue
        
        # if there is no common prefix or not long enough
        common_prefix = get_common_prefix(labels[error_index-1], labels[error_index+1])
        if len(common_prefix) == 0 or len(common_prefix) < prefix_len_th:
            new_error_index.append(error_index)
            continue
        
        error_label = labels[error_index]
        for i in range(len(common_prefix)):
            if (error_label[i] != common_prefix[i]) and (error_label[i] not in potential_errors[common_prefix[i]]):
                new_error_index.append(error_index)
                break
    return new_error_index

if __name__ == "__main__":
    labels = ["ADCDEFG", "ABCDEFF", "ABCDBFG", "ABCDEHJ", "ABCDEFF"]
    err_index = [0, 2, 4]
    new_err_index = error_correct(labels, err_index, 4)
    print(new_err_index)
