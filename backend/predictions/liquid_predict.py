import cv2
import numpy as np
import joblib
from scipy.stats import skew, kurtosis

model = joblib.load('models/model_liquid.joblib')
label_encoder = joblib.load('models/label_encoder_liquid.joblib')

def color_features_liquid_predict(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 75, 255, cv2.THRESH_BINARY_INV)
    circles = cv2.HoughCircles(
        binary,
        cv2.HOUGH_GRADIENT, dp=1.2, minDist=100, param1=50, param2=30, minRadius=0, maxRadius=0
    )
    mask = np.zeros_like(gray)
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv2.circle(mask, (x, y), r, 255, thickness=-1)
            break
    image_copy = np.full_like(image, (255, 255, 255), dtype=np.uint8)
    image_copy[mask == 255] = image[mask == 255]
    height, width, _ = image_copy.shape
    center_x, center_y = width // 2, height // 2
    margin_x = int(width * 0.15)
    margin_y = int(height * 0.15)
    start_x = max(center_x - margin_x, 0)
    end_x = min(center_x + margin_x, width)
    start_y = max(center_y - margin_y, 0)
    end_y = min(center_y + margin_y, height)
    cropped_image = image_copy[start_y:end_y, start_x:end_x]
    masked_image = cropped_image[(cropped_image[:, :, 0] < 255) |
                                    (cropped_image[:, :, 1] < 255) |
                                    (cropped_image[:, :, 2] < 255)]

    masked_pixels = masked_image.reshape(-1, 3)

    image_copy_rgb = cv2.cvtColor(masked_pixels.reshape(-1, 1, 3), cv2.COLOR_BGR2RGB).reshape(-1, 3)
    mean_bgr = np.mean(image_copy_rgb, axis=0)
    median_bgr = np.median(image_copy_rgb, axis=0)
    std_bgr = np.std(image_copy_rgb, axis=0)
    skew_bgr   = skew(image_copy_rgb, axis=0, bias=False)
    kurt_bgr   = kurtosis(image_copy_rgb, axis=0, bias=False)

    image_copy_hsb = cv2.cvtColor(masked_pixels.reshape(-1, 1, 3), cv2.COLOR_BGR2HSV).reshape(-1, 3)
    mean_hsv = np.mean(image_copy_hsb, axis=0)
    median_hsv = np.median(image_copy_hsb, axis=0)
    std_hsv = np.std(image_copy_hsb, axis=0)
    skew_hsv   = skew(image_copy_hsb, axis=0, bias=False)
    kurt_hsv   = kurtosis(image_copy_hsb, axis=0, bias=False)

    image_copy_lab = cv2.cvtColor(masked_pixels.reshape(-1, 1, 3), cv2.COLOR_BGR2LAB).reshape(-1, 3)
    mean_lab   = np.mean(image_copy_lab, axis=0)
    median_lab = np.median(image_copy_lab, axis=0)
    std_lab    = np.std(image_copy_lab, axis=0)
    skew_lab   = skew(image_copy_lab, axis=0, bias=False)
    kurt_lab   = kurtosis(image_copy_lab, axis=0, bias=False)

    non_white_pixels_ycc = cv2.cvtColor(masked_pixels.reshape(-1, 1, 3), cv2.COLOR_BGR2YCrCb).reshape(-1, 3)
    mean_ycc = np.mean(non_white_pixels_ycc, axis=0)
    median_ycc = np.median(non_white_pixels_ycc, axis=0)
    std_ycc = np.std(non_white_pixels_ycc, axis=0)
    skew_ycc = skew(non_white_pixels_ycc, axis=0, bias=False)
    kurt_ycc = kurtosis(non_white_pixels_ycc, axis=0, bias=False)

    features = [mean_bgr.tolist()[0], mean_bgr.tolist()[1], mean_bgr.tolist()[2],
                median_bgr.tolist()[0], median_bgr.tolist()[1], median_bgr.tolist()[2],
                std_bgr.tolist()[0], std_bgr.tolist()[1], std_bgr.tolist()[2],
                skew_bgr.tolist()[0], skew_bgr.tolist()[1], skew_bgr.tolist()[2],
                kurt_bgr.tolist()[0], kurt_bgr.tolist()[1], kurt_bgr.tolist()[2],
                mean_hsv.tolist()[0], mean_hsv.tolist()[1], mean_hsv.tolist()[2],
                median_hsv.tolist()[0], median_hsv.tolist()[1], median_hsv.tolist()[2],
                std_hsv.tolist()[0], std_hsv.tolist()[1], std_hsv.tolist()[2],
                skew_hsv.tolist()[0], skew_hsv.tolist()[1], skew_hsv.tolist()[2],
                kurt_hsv.tolist()[0], kurt_hsv.tolist()[1], kurt_hsv.tolist()[2],
                mean_lab.tolist()[0], mean_lab.tolist()[1], mean_lab.tolist()[2],
                median_lab.tolist()[0], median_lab.tolist()[1], median_lab.tolist()[2],
                std_lab.tolist()[0], std_lab.tolist()[1], std_lab.tolist()[2],
                skew_lab.tolist()[0], skew_lab.tolist()[1], skew_lab.tolist()[2],
                kurt_lab.tolist()[0], kurt_lab.tolist()[1], kurt_lab.tolist()[2],
                mean_ycc.tolist()[0], mean_ycc.tolist()[1], mean_ycc.tolist()[2],
                median_ycc.tolist()[0], median_ycc.tolist()[1], median_ycc.tolist()[2],
                std_ycc.tolist()[0], std_ycc.tolist()[1], std_ycc.tolist()[2],
                skew_ycc.tolist()[0], skew_ycc.tolist()[1], skew_ycc.tolist()[2],
                kurt_ycc.tolist()[0], kurt_ycc.tolist()[1], kurt_ycc.tolist()[2]]

    y_pred = model.predict([features])
    elevation = label_encoder.inverse_transform([y_pred[0]])
    return elevation[0]