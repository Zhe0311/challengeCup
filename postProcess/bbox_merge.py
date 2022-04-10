"""
    Background: booklabel contains two or more lines of text, 
    but OCR models just return bounding boxes for individual lines.
    Therefore, we need to merge lines into labels using spatial heuristics.

    top_level function: merge_bboxes
"""

from copy import copy, deepcopy
from functools import cmp_to_key
from typing import List, Tuple

# define types
Point = Tuple[int, int] # row, column
BBox = Tuple[Point, Point, Point, Point] # 4-point boinding-box
BookLabel = List[BBox] # a booklabel contains two or more lines of texts
Coordinate = Tuple[int, int, int, int] # rmin, rmax, cmin, cmax


"""
def get_coordinates_of_bbox(bbox: BBox) -> Coordinate:
    rmin = min(p[0] for p in bbox)
    rmax = max(p[0] for p in bbox)
    cmin = min(p[1] for p in bbox)
    cmax = max(p[1] for p in bbox)
    return rmin, rmax, cmin, cmax
"""

def get_coordinates(bbox: dict) -> Coordinate:
    region = bbox['text_region']
    rmin = min(region[0][0], region[1][0], region[2][0], region[3][0])
    rmax = max(region[0][0], region[1][0], region[2][0], region[3][0])
    cmin = min(region[0][1], region[1][1], region[2][1], region[3][1])
    cmax = max(region[0][1], region[1][1], region[2][1], region[3][1])
    return (rmin, rmax, cmin, cmax)

# for sorting
def cmp_bbox_by_cmin(bbox_lfs: BBox, bbox_rhs: BBox) -> int:
    _, _, cmin_lhs, _ = get_coordinates(bbox_lfs)
    _, _, cmin_rhs, _ = get_coordinates(bbox_rhs)
    if cmin_lhs < cmin_rhs:
        return -1
    elif cmin_lhs > cmin_rhs:
        return 1
    else:
        return 0

def cmp_bbox_by_rmin(bbox_lfs: BBox, bbox_rhs: BBox) -> int:
    rmin_lhs, _, _, _ = get_coordinates(bbox_lfs)
    rmin_rhs, _, _, _ = get_coordinates(bbox_rhs)
    if rmin_lhs < rmin_rhs:
        return -1
    elif rmin_lhs < rmin_rhs:
        return 1
    else:
        return 0

# judge if a bbox is of horizontal text or vertical by aspect ratio
def is_row_box(bbox: BBox) -> bool:
    rmin, rmax, cmin, cmax = get_coordinates(bbox)
    return abs(rmax - rmin) < abs(cmax - cmin)

# judge if two bbox belong to the same label by their overlap ratio
# which is defined as: overlap_ratio = overlap_length_of_a_and_b / min(length_of_a, length_of_b)
def could_merge(boxa: BBox, boxb: BBox, overlap_th=0.7, gap_th=1.) -> bool:
    if (is_row_box(boxa) != is_row_box(boxb)):
        return False

    rmin_a, rmax_a, cmin_a, cmax_a = get_coordinates(boxa)
    rmin_b, rmax_b, cmin_b, cmax_b = get_coordinates(boxb)

    if is_row_box(boxa):
        col_overlap_ratio = min(cmax_b - cmin_a, cmax_a - cmin_b) \
                          / min(cmax_a - cmin_a ,cmax_b - cmin_b)
        text_height = min(rmax_a - rmin_a, rmax_b - rmin_b)
        line_gap = min(abs(rmax_b - rmin_a), abs(rmax_a - rmin_b))
        return col_overlap_ratio > overlap_th and line_gap <  gap_th * text_height
    
    else:
        row_overlap_ratio = min(rmax_b - rmin_a, rmax_a - rmin_b) \
                          / min(rmax_a - rmin_a, rmax_b - rmin_b)
        text_width = min(cmax_a - cmin_a, cmax_b - cmin_b)
        line_gap = min(abs(cmax_b - cmin_a), abs(cmax_a - cmin_b))
        return row_overlap_ratio > overlap_th and line_gap < gap_th * text_width


# merge bboxes of individual lines into labels
# algorithm: sort bboxes by their minimum column index
#            and then merge greedily
def merge_bboxes(bboxes: List[BBox]) -> List[BookLabel]:
    bboxes = copy(bboxes)
    bboxes.sort(key=cmp_to_key(cmp_bbox_by_cmin))
    booklabels = []
    while bboxes: # not empty
        label = []
        box = bboxes[0]
        label.append(box)
        bboxes.pop(0) # pop_front
        while(bboxes and could_merge(box, bboxes[0])):
            label.append(bboxes[0])
            bboxes.pop(0)
        
        if is_row_box(box):
            label.sort(key=cmp_to_key(cmp_bbox_by_rmin))
        else:
            label.sort(key=cmp_to_key(cmp_bbox_by_cmin), reverse=True)

        booklabels.append(label)
    
    return booklabels


def xy2rc(ocr_results: List[dict]) -> List[dict]:
    ocr_results = deepcopy(ocr_results)
    for item in ocr_results:
        region = item['text_region']
        for p in region:
            p[0], p[1] = p[1], p[0] # swap x and y
    
    return ocr_results


def extract_labels(merged_dicts: List[List[dict]]) -> List[str]:
    labels = []
    for dicts in merged_dicts:
        lb = ""
        for dict in dicts:
            lb += dict['text'] + '\n'
        lb = lb[:-1] # drop last '\n'
        labels.append(lb)
    return labels

def parse_ocr_result(ocr_results) -> List[str]:
    ocr_results = ocr_results[0]
    ocr_results = xy2rc(ocr_results)
    merged_dicts = merge_bboxes(ocr_results)
    labels = extract_labels(merged_dicts)     
    return labels

# demo of usage
if __name__ == "__main__":
    # label 0
    box00 = [[1, 1], [1, 5], [3, 1], [3, 5]]
    box01 = [[5, 1], [5, 5], [7, 1], [7, 5]]
    # label 1
    box10 = [[1, 10], [1, 20], [3, 10], [3, 21]]
    box11 = [[6, 11], [6, 25], [8, 9], [8, 25]]

    ocr_results = [[{'confidence': 0.9982509016990662, 'text': 'S703A8', 'text_region': [[1930, 1236], [2022, 1236], [2022, 1488], [1930, 1488]]}, {'confidence': 0.9765312075614929, 'text': 'K837.127.5', 'text_region': [[1475, 1250], [1578, 1254], [1565, 1657], [1462, 1653]]}, {'confidence': 0.9625622034072876, 'text': 'K837.127.5', 'text_region': [[2018, 1244], [2109, 1244], [2109, 1628], [2018, 1628]]}, {'confidence': 0.9727174043655396, 'text': 'S703A7B3', 'text_region': [[1383, 1259], [1474, 1259], [1474, 1578], [1383, 1578]]}, {'confidence': 0.9559917449951172, 'text': 'S703A6', 'text_region': [[375, 1305], [474, 1317], [445, 1582], [347, 1571]]}, {'confidence': 0.9957461357116699, 'text': 'K837.127.5', 'text_region': [[463, 1309], [569, 1321], [529, 1722], [422, 1711]]}, {'confidence': 0.9975822567939758, 'text': 'S703A7', 'text_region': [[685, 1320], [780, 1324], [770, 1587], [675, 1583]]}, {'confidence': 0.9530078172683716, 'text': 'K837.127.5', 'text_region': [[777, 1327], [883, 1334], [861, 1731], [754, 1725]]}, {'confidence': 0.9372909069061279, 'text': 'S703A2', 'text_region': [[101, 1338], [200, 1347], [178, 1619], [79, 1611]]}, {'confidence': 0.9665063619613647, 'text': 'K837.127.5', 'text_region': [[197, 1340], [304, 1352], [259, 1762], [152, 1749]]}, {'confidence': 0.9967876672744751, 'text': 'S703A7B2', 'text_region': [[1082, 1335], [1173, 1332], [1183, 1677], [1091, 1680]]}, {'confidence': 0.9961230158805847, 'text': 'K837.127.5', 'text_region': [[1174, 1341], [1265, 1341], [1265, 1726], [1174, 1726]]}, {'confidence': 0.9452852606773376, 'text': 'X122A3', 'text_region': [[2963, 1344], [3042, 1339], [3057, 1586], [2977, 1591]]}, {'confidence': 0.9959268569946289, 'text': 'S703A7B4', 'text_region': [[1652, 1350], [1743, 1348], [1753, 1681], [1661, 1684]]}, {'confidence': 0.9191320538520813, 'text': 'K837.127.5', 'text_region': [[1736, 1355], [1827, 1351], [1840, 1739], [1749, 1742]]}, {'confidence': 0.9975250363349915, 'text': 'K837.127.5', 'text_region': [[3035, 1349], [3126, 1343], [3148, 1718], [3057, 1723]]}, {'confidence': 0.9959003329277039, 'text': 'K837.127.5', 'text_region': [[2176, 1390], [2536, 1404], [2532, 1509], [2172, 1495]]}, {'confidence': 0.9778413772583008, 'text': 'K837.127.5', 'text_region': [[2565, 1430], [2907, 1430], [2907, 1535], [2565, 1535]]}, {'confidence': 0.9894635081291199, 'text': 'K837.127.5', 'text_region': [[3257, 1430], [3576, 1430], [3576, 1523], [3257, 1523]]}, {'confidence': 0.997714102268219, 'text': 'W497', 'text_region': [[2185, 1488], [2360, 1488], [2360, 1586], [2185, 1586]]}, {'confidence': 0.9507190585136414, 'text': 'K122A2', 'text_region': [[2573, 1516], [2797, 1516], [2797, 1613], [2573, 1613]]}, {'confidence': 0.9400584697723389, 'text': 'X122A5C3', 'text_region': [[3264, 1512], [3542, 1512], [3542, 1605], [3264, 1605]]}]]
    labels = parse_ocr_result(ocr_results)
    print(labels)
