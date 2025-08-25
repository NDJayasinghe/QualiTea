import cv2
import numpy as np
import joblib
from scipy.stats import skew, kurtosis

model = joblib.load('models/model_infusion.joblib')
label_encoder = joblib.load('models/label_encoder_infusion.joblib')

def color_features_infusion_predict(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    min_contour_area = 300
    white_background = np.full_like(image, (255, 255, 255), dtype=np.uint8)
    mask = np.zeros_like(gray)
    for i, contour in enumerate(contours):
        if cv2.contourArea(contour) > min_contour_area:
            cv2.drawContours(mask, [contour], -1, 255, cv2.FILLED)
    white_background[mask == 255] = image[mask == 255]
    for i, contour in enumerate(contours):
        if cv2.contourArea(contour) > min_contour_area:
            if hierarchy[0][i][3] != -1:
                cv2.drawContours(white_background, [contour], -1, (255, 255, 255), cv2.FILLED)
    masked_pixels = white_background[mask != 0]
    non_white_pixels = masked_pixels[(masked_pixels[:, 0] < 255) | (masked_pixels[:, 1] < 255) | (masked_pixels[:, 2] < 255)]
    non_white_pixels_rgb = cv2.cvtColor(non_white_pixels.reshape(-1, 1, 3), cv2.COLOR_BGR2RGB).reshape(-1, 3)
    mean_bgr = np.mean(non_white_pixels_rgb, axis=0)
    median_bgr = np.median(non_white_pixels_rgb, axis=0)
    std_bgr = np.std(non_white_pixels_rgb, axis=0)
    skew_bgr = skew(non_white_pixels_rgb, axis=0, bias=False)
    kurt_bgr = kurtosis(non_white_pixels_rgb, axis=0, bias=False)

    non_white_pixels_hsb = cv2.cvtColor(non_white_pixels.reshape(-1, 1, 3), cv2.COLOR_BGR2HSV).reshape(-1, 3)
    mean_hsv = np.mean(non_white_pixels_hsb, axis=0)
    median_hsv = np.median(non_white_pixels_hsb, axis=0)
    std_hsv = np.std(non_white_pixels_hsb, axis=0)
    skew_hsv   = skew(non_white_pixels_hsb, axis=0, bias=False)
    kurt_hsv   = kurtosis(non_white_pixels_hsb, axis=0, bias=False)

    non_white_pixels_lab = cv2.cvtColor(non_white_pixels.reshape(-1, 1, 3), cv2.COLOR_BGR2LAB).reshape(-1, 3)
    mean_lab = np.mean(non_white_pixels_lab, axis=0)
    median_lab = np.median(non_white_pixels_lab, axis=0)
    std_lab = np.std(non_white_pixels_lab, axis=0)
    skew_lab = skew(non_white_pixels_lab, axis=0, bias=False)
    kurt_lab = kurtosis(non_white_pixels_lab, axis=0, bias=False)

    non_white_pixels_ycc = cv2.cvtColor(non_white_pixels.reshape(-1, 1, 3), cv2.COLOR_BGR2YCrCb).reshape(-1, 3)
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
    t_quality = label_encoder.inverse_transform([y_pred[0]])
    return t_quality[0]