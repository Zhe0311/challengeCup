from src_booklabel import compare_label, order_judge
import cv2

def inversion_number(labels :list) -> int:
    """calculate the inversion number of label list"""
    cnt = 0
    for i in range(len(labels)-1):
        for j in range(i+1, len(labels)):
            if compare_label(labels[i], labels[j]) == 1:
                cnt += 1
    return cnt

def get_error_index(labels :list) -> int:
    """get the index of the label causes the most inversion number"""
    smallest_inversion_number = (1+len(labels))*len(labels)/2
    index = 0
    for i in range(len(labels)):
        if inversion_number(labels[0: i] + labels[i+1: len(labels)]) < smallest_inversion_number:
            smallest_inversion_number = inversion_number(labels[0: i] + labels[i+1: len(labels)])
            index = i
    return index

def get_error_index_list(labels :list) -> list:
    mask = [1] * len(labels)
    error_index = []
    masked_labels = labels

    while not order_judge(masked_labels):
        index_masked = get_error_index(masked_labels)

        # map: index of masked labels -> index of original labels
        cnt = -1
        index_original = 0
        for i in range(len(labels)):
            if mask[i]:
                cnt += 1
            if cnt == index_masked:
                index_original = i
                error_index.append(index_original)
                break
            
        mask[index_original] = False
        masked_labels = [new_labels for new_labels, m in zip(labels, mask) if m]
    
    return error_index
        
# def draw_err_books(err_indexs: list, position_info: list, pic, thickness=3, spacing=10):
#     img = img.copy()
#     for err_index in err_indexs:
#         for region in position_info[err_index]['text_region']:
#             img = cv2.rectangle(img, (region[3][0], region[3][1]), (region[1][0], region[1][1]), color=(0, 0, 255), thickness=thickness)
#             cv2.putText(img,label,(cmin,rmax),cv2.FONT_HERSHEY_COMPLEX, 1.0, (255,255, 0), 2)   
#     return img



if __name__ == "__main__":
    labels = ["999", "123", "888", "234", "345", "567", "456"]
    print(inversion_number(labels))
    print(" ", labels)
    print(get_error_index_list(labels))



    