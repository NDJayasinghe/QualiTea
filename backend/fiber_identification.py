import cv2
import numpy as np

# ---- Helper Functions ----
def calculate_longest_distance(contour):
    max_distance = 0
    for i in range(len(contour)):
        for j in range(i + 1, len(contour)):
            distance = np.linalg.norm(contour[i][0] - contour[j][0])
            if distance > max_distance:
                max_distance = distance
    return max_distance

def is_contour_touching_boundary(contour, image_shape):
    for point in contour:
        if point[0][0] <= 0 or point[0][0] >= image_shape[1] - 1 or point[0][1] <= 0 or point[0][1] >= image_shape[0] - 1:
            return True
    return False

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
def identify_fiber_in_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    if hierarchy is None:
        return image, {"error": "No contours found"}

    # Parameters
    min_contour_area = 300
    min_fiber_area = 300
    max_fiber_area = 905
    min_fiber_height = 75
    elongation_lower = 1.1
    elongation_upper = 5.5
    pa_ratio_lower = 0.20
    pa_ratio_upper = 0.60

    segmented_image = np.full_like(image, 255, dtype=np.uint8)
    thin_particles_image = np.full_like(image, 255, dtype=np.uint8)
    mask = np.zeros_like(gray)

    thin_particles = []

    box_contour = get_largest_box_contour(contours, image.shape)

    for i, contour in enumerate(contours):
        if is_inside_box(contour, box_contour):
            continue
        if cv2.contourArea(contour) > min_contour_area:
            cv2.drawContours(mask, [contour], -1, 255, cv2.FILLED)
    segmented_image[mask == 255] = image[mask == 255]

    for i, contour in enumerate(contours):
        if is_inside_box(contour, box_contour):
            continue

        area = cv2.contourArea(contour)
        if area <= min_contour_area:
            continue

        cv2.drawContours(segmented_image, [contour], -1, (0, 255, 0), 2)
        if hierarchy[0][i][3] != -1:
            cv2.drawContours(segmented_image, [contour], -1, (255, 255, 255), cv2.FILLED)

        rect = cv2.minAreaRect(contour)
        width, height = rect[1]
        if min(width, height) == 0:
            continue
        elongation = max(width, height) / min(width, height)

        perimeter = cv2.arcLength(contour, True)
        pa_ratio = perimeter / area if area != 0 else 0

        height_longest = calculate_longest_distance(contour)

        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            cX, cY = contour[0][0][0], contour[0][0][1]

        text = f"A:{int(area)} E:{elongation:.1f} H:{int(height_longest)} P/A:{pa_ratio:.2f}"
        cv2.putText(segmented_image, text, (cX, cY),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

        if (
            min_fiber_area <= area <= max_fiber_area and
            elongation_lower <= elongation <= elongation_upper and
            pa_ratio_lower <= pa_ratio <= pa_ratio_upper and
            height_longest > min_fiber_height and
            hierarchy[0][i][3] == -1 and
            not is_contour_touching_boundary(contour, image.shape)
        ):
            thin_particles.append(contour)
            mask = np.zeros_like(gray)
            cv2.drawContours(mask, [contour], -1, 255, cv2.FILLED)
            thin_particles_image[mask == 255] = image[mask == 255]
            cv2.putText(thin_particles_image, text, (cX, cY),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    total_particles = sum(
        1 for i in range(len(contours))
        if (
            cv2.contourArea(contours[i]) > min_contour_area and
            not is_contour_touching_boundary(contours[i], image.shape) and
            hierarchy[0][i][3] == -1 and
            not is_inside_box(contours[i], box_contour)
        )
    )

    average_ratio = len(thin_particles) / total_particles if total_particles > 0 else 0
    fiber_percentage = average_ratio * 100

    stats = {
        "number_of_thin_particles": len(thin_particles),
        "total_number_of_particles": total_particles,
        "fiber_percentage": round(fiber_percentage, 2)
    }

    return thin_particles_image, stats
