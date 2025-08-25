import cv2
import numpy as np

# ---- Helper Functions ----

def is_contour_touching_boundary(contour, image_shape):
    for point in contour:
        if point[0][0] <= 0 or point[0][0] >= image_shape[1] - 1 or point[0][1] <= 0 or point[0][1] >= image_shape[0] - 1:
            return True
    return False

def is_contour_inner(contour_index, hierarchy):
    return hierarchy[0][contour_index][3] != -1

def get_largest_box_contour(contours, image_shape):
    max_area = 0
    best_box = None
    for cnt in contours:
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)
        is_near_border = any([
            np.any(cnt[:, 0, 0] < 10),
            np.any(cnt[:, 0, 1] < 10),
            np.any(cnt[:, 0, 0] > image_shape[1] - 10),
            np.any(cnt[:, 0, 1] > image_shape[0] - 10)
        ])
        if len(approx) == 4 and area > max_area and is_near_border:
            max_area = area
            best_box = cnt
    return best_box

def is_inside_box(contour, box_contour):
    if box_contour is None or len(contour) == 0 or len(contour[0]) == 0:
        return False
    try:
        test_point = contour[0][0]
        if len(test_point) != 2:
            return False
        return cv2.pointPolygonTest(box_contour, tuple(test_point), False) >= 0
    except:
        return False

# ---- Main Function ----

def identify_stroke_in_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    if hierarchy is None:
        return image, {"error": "No contours found"}

    # ---- Parameters ----
    r_lower_bound, r_upper_bound = 90, 240
    g_lower_bound, g_upper_bound = 50, 210
    b_lower_bound, b_upper_bound = 20, 160
    gray_diff_threshold = 15

    min_contour_area = 50
    contour_areas = [cv2.contourArea(c) for c in contours if cv2.contourArea(c) > 0]
    percentile_90_area = np.percentile(contour_areas, 90) if contour_areas else 1000
    large_contour_area = percentile_90_area * 1.5

    box_contour = get_largest_box_contour(contours, image.shape)

    filtered_contours = []
    all_r_values, all_g_values, all_b_values = [], [], []
    brown_r_values, brown_g_values, brown_b_values = [], [], []

    for i, contour in enumerate(contours):
        contour_area = cv2.contourArea(contour)

        if (min_contour_area < contour_area < large_contour_area and
            not is_contour_inner(i, hierarchy) and
            not is_inside_box(contour, box_contour) and
            not is_contour_touching_boundary(contour, image.shape)):

            mask = np.zeros_like(gray)
            cv2.drawContours(mask, [contour], -1, 255, cv2.FILLED)

            b_values = image[mask == 255][:, 0]
            g_values = image[mask == 255][:, 1]
            r_values = image[mask == 255][:, 2]

            mean_r = np.mean(r_values)
            mean_g = np.mean(g_values)
            mean_b = np.mean(b_values)

            all_r_values.extend(r_values)
            all_g_values.extend(g_values)
            all_b_values.extend(b_values)

            if (r_lower_bound <= mean_r <= r_upper_bound and
                g_lower_bound <= mean_g <= g_upper_bound and
                b_lower_bound <= mean_b <= b_upper_bound and
                mean_r > mean_g - 10 and mean_g > mean_b - 10 and
                (abs(mean_r - mean_g) > gray_diff_threshold or
                 abs(mean_g - mean_b) > gray_diff_threshold or
                 abs(mean_r - mean_b) > gray_diff_threshold)):

                filtered_contours.append(contour)
                brown_r_values.extend(r_values)
                brown_g_values.extend(g_values)
                brown_b_values.extend(b_values)

    # ---- Create Output Image ----
    filtered_background = np.full_like(image, (255, 255, 255), dtype=np.uint8)
    for contour in filtered_contours:
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, [contour], -1, 255, cv2.FILLED)
        filtered_background[mask == 255] = image[mask == 255]

    # ---- Stats ----
    number_of_external_contours = sum(
        1 for i in range(len(contours))
        if (min_contour_area < cv2.contourArea(contours[i]) < large_contour_area and
            not is_contour_inner(i, hierarchy) and
            not is_inside_box(contours[i], box_contour) and
            not is_contour_touching_boundary(contours[i], image.shape))
    )

    brown_particle_ratio = (
        len(filtered_contours) / number_of_external_contours * 100
        if number_of_external_contours > 0 else 0
    )

    average_all_r = np.mean(all_r_values) if all_r_values else 0
    average_all_g = np.mean(all_g_values) if all_g_values else 0
    average_all_b = np.mean(all_b_values) if all_b_values else 0

    average_brown_r = np.mean(brown_r_values) if brown_r_values else 0
    average_brown_g = np.mean(brown_g_values) if brown_g_values else 0
    average_brown_b = np.mean(brown_b_values) if brown_b_values else 0

    stats = {
        "number_of_external_contours": number_of_external_contours,
        "number_of_brown_particles": len(filtered_contours),
        "brown_particle_ratio": round(brown_particle_ratio, 2),
        "average_all_r": round(average_all_r, 2),
        "average_all_g": round(average_all_g, 2),
        "average_all_b": round(average_all_b, 2),
        "average_brown_r": round(average_brown_r, 2),
        "average_brown_g": round(average_brown_g, 2),
        "average_brown_b": round(average_brown_b, 2)
    }

    return filtered_background, stats
