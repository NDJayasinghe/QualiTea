import cv2
import numpy as np
import joblib
from scipy.stats import skew, kurtosis
from sklearn.cluster import KMeans
import os

# Load trained model, scaler, and label encoder
model = joblib.load('models/model_particle_color_size.joblib')
scaler = joblib.load('models/scaler_particle_color_size.joblib')
label_encoder = joblib.load('models/label_encoder_particle_color_size.joblib')


def is_contour_touching_boundary(contour, image_shape):
    for point in contour:
        if point[0][0] <= 0 or point[0][0] >= image_shape[1] - 1 or point[0][1] <= 0 or point[0][1] >= image_shape[0] - 1:
            return True
    return False


def process_color(image_path, min_contour_area=300):
    image = cv2.imread(image_path)
    if image is None:
        return {}

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    if hierarchy is None or len(contours) == 0:
        return {}

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    all_r, all_g, all_b, all_h, all_s, all_v, all_brightness = [], [], [], [], [], [], []

    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area > min_contour_area and hierarchy[0][i][3] == -1 and not is_contour_touching_boundary(contour, image.shape):
            mask = np.zeros_like(gray)
            cv2.drawContours(mask, [contour], -1, 255, cv2.FILLED)

            r = image[:, :, 2][mask == 255]
            g = image[:, :, 1][mask == 255]
            b = image[:, :, 0][mask == 255]
            h = hsv_image[:, :, 0][mask == 255]
            s = hsv_image[:, :, 1][mask == 255]
            v = hsv_image[:, :, 2][mask == 255]

            if r.size == 0:
                continue

            all_r.append(r); all_g.append(g); all_b.append(b)
            all_h.append(h); all_s.append(s); all_v.append(v)
            all_brightness.append(v)

    if not all_r:
        return {}

    return {
        'Mean R': np.mean(np.concatenate(all_r)),
        'Median R': np.median(np.concatenate(all_r)),
        'Std Dev R': np.std(np.concatenate(all_r)),
        'Mean G': np.mean(np.concatenate(all_g)),
        'Median G': np.median(np.concatenate(all_g)),
        'Std Dev G': np.std(np.concatenate(all_g)),
        'Mean B': np.mean(np.concatenate(all_b)),
        'Median B': np.median(np.concatenate(all_b)),
        'Std Dev B': np.std(np.concatenate(all_b)),
        'Mean H': np.mean(np.concatenate(all_h)),
        'Median H': np.median(np.concatenate(all_h)),
        'Std Dev H': np.std(np.concatenate(all_h)),
        'Mean S': np.mean(np.concatenate(all_s)),
        'Median S': np.median(np.concatenate(all_s)),
        'Std Dev S': np.std(np.concatenate(all_s)),
        'Mean V': np.mean(np.concatenate(all_v)),
        'Median V': np.median(np.concatenate(all_v)),
        'Std Dev V': np.std(np.concatenate(all_v)),
        'Mean Brightness': np.mean(np.concatenate(all_brightness)),
        'Median Brightness': np.median(np.concatenate(all_brightness)),
        'Std Dev Brightness': np.std(np.concatenate(all_brightness)),
    }


def get_contour_features(contour):
    area = cv2.contourArea(contour)
    x, y, w, h = cv2.boundingRect(contour)
    aspect_ratio = float(w) / h if h != 0 else 0
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    solidity = float(area) / hull_area if hull_area != 0 else 0
    extent = float(area) / (w * h) if w * h != 0 else 0
    perimeter = cv2.arcLength(contour, True)
    roundness = (4 * np.pi * area) / (perimeter ** 2) if perimeter != 0 else 0
    compactness = (perimeter ** 2) / area if area != 0 else 0
    return [area, w, h, aspect_ratio, solidity, extent, perimeter, roundness, compactness]


def cluster_particles(features):
    if len(features) < 7:
        return [0] * len(features), set()

    X = np.array(features)
    kmeans = KMeans(n_clusters=7, random_state=42).fit(X)
    labels = kmeans.labels_

    cluster_mean_areas = [(i, X[labels == i][:, 0].mean()) for i in range(7)]
    sorted_clusters = sorted(cluster_mean_areas, key=lambda x: x[1])

    # Define "small particle" clusters
    small_clusters = {sorted_clusters[1][0], sorted_clusters[2][0], sorted_clusters[3][0]}
    return labels, small_clusters


def process_size(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    features = []
    valid_contours = []
    for contour in contours:
        if cv2.contourArea(contour) > 0:
            features.append(get_contour_features(contour))
            valid_contours.append(contour)

    if not features:
        return {}

    labels, small_clusters = cluster_particles(features)

    small_areas, small_widths, small_heights = [], [], []
    small_aspects, small_solidities, small_extents = [], [], []
    small_perimeters, small_roundness, small_compactness = [], [], []

    for i, f in enumerate(features):
        if hierarchy[0][i][3] == -1 and not is_contour_touching_boundary(valid_contours[i], image.shape):
            if labels[i] in small_clusters:
                area, w, h, ar, sol, ext, peri, rnd, comp = f
                small_areas.append(area)
                small_widths.append(w)
                small_heights.append(h)
                small_aspects.append(ar)
                small_solidities.append(sol)
                small_extents.append(ext)
                small_perimeters.append(peri)
                small_roundness.append(rnd)
                small_compactness.append(comp)

    if not small_areas:
        return {}

    return {
        'Small Particle Count': len(small_areas),
        'Total Small Particle Area': sum(small_areas),
        'Mean Small Particle Area': np.mean(small_areas),
        'Median Small Particle Area': np.median(small_areas),
        'Std Dev Small Particle Area': np.std(small_areas),
        'Skewness Small Particle Area': skew(small_areas) if len(small_areas) > 2 else 0,
        'Kurtosis Small Particle Area': kurtosis(small_areas) if len(small_areas) > 2 else 0,
        'Mean Width': np.mean(small_widths),
        'Median Width': np.median(small_widths),
        'Std Dev Width': np.std(small_widths),
        'Mean Height': np.mean(small_heights),
        'Median Height': np.median(small_heights),
        'Std Dev Height': np.std(small_heights),
        'Mean Aspect Ratio': np.mean(small_aspects),
        'Std Aspect Ratio': np.std(small_aspects),
        'Mean Solidity': np.mean(small_solidities),
        'Std Solidity': np.std(small_solidities),
        'Mean Extent': np.mean(small_extents),
        'Std Extent': np.std(small_extents),
        'Mean Perimeter': np.mean(small_perimeters),
        'Std Perimeter': np.std(small_perimeters),
        'Mean Roundness': np.mean(small_roundness),
        'Std Roundness': np.std(small_roundness),
        'Mean Compactness': np.mean(small_compactness),
        'Std Compactness': np.std(small_compactness)
    }


def extract_combined_features(image_path):
    color_feats = process_color(image_path)
    size_feats = process_size(image_path)

    if not color_feats or not size_feats:
        return None

    return list(color_feats.values()) + list(size_feats.values())


def predict_tea_variant_from_image(image_path):
    features = extract_combined_features(image_path)
    if features is None:
        return "Error: Failed to extract features"

    scaled = scaler.transform([features])
    pred = model.predict(scaled)
    return label_encoder.inverse_transform(pred)[0]


if __name__ == "__main__":
    image_path = "test_images/sample.jpg"
    print("Predicted Tea Variant:", predict_tea_variant_from_image(image_path))
