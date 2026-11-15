import sys
import os
import cv2
import requests

def main():
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Fallback to test image in project if available
        candidate = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "workflow_diagram.jpg"))
        if os.path.exists(candidate):
            image_path = candidate
        else:
            print("Usage: python test_detect.py <path_to_image>")
            sys.exit(1)

    image_path = os.path.abspath(image_path)
    if not os.path.exists(image_path):
        print(f"Error: File not found: {image_path}")
        sys.exit(1)

    url = "http://localhost:8000/detect"
    print(f"Submitting image to {url}: {image_path}")

    with open(image_path, "rb") as f:
        files = {"file": (os.path.basename(image_path), f, "image/jpeg")}
        try:
            resp = requests.post(url, files=files, timeout=30)
        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to YOLO-World server at http://localhost:8000.")
            print("Ensure the server is running with: uvicorn main:app --port 8000")
            sys.exit(1)

    if resp.status_code != 200:
        print(f"Error: Server returned HTTP {resp.status_code}: {resp.text}")
        sys.exit(1)

    data = resp.json()
    time_ms = data.get("time_ms", 0)
    obstacles = data.get("obstacles", [])
    model_name = data.get("model", "yolo-world")

    print(f"\n[{model_name}] Detection completed in {time_ms} ms. Found {len(obstacles)} obstacle(s):\n")
    print(f"{'Label':<25} {'Score':<8} {'Box (x, y, w, h)':<30}")
    print("-" * 65)

    img = cv2.imread(image_path)
    if img is None:
        print("Warning: Could not read image with OpenCV to create annotated copy.")
        return

    img_h, img_w = img.shape[:2]

    for obs in obstacles:
        label = obs.get("label", "unknown")
        score = obs.get("score", 0.0)
        x_norm, y_norm = obs.get("x", 0.0), obs.get("y", 0.0)
        w_norm, h_norm = obs.get("w", 0.0), obs.get("h", 0.0)

        box_str = f"({x_norm:.3f}, {y_norm:.3f}, {w_norm:.3f}, {h_norm:.3f})"
        print(f"{label:<25} {score:<8.3f} {box_str:<30}")

        # Pixel coordinates
        x1 = int(x_norm * img_w)
        y1 = int(y_norm * img_h)
        x2 = int((x_norm + w_norm) * img_w)
        y2 = int((y_norm + h_norm) * img_h)

        # Draw red bounding box
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 235), 2)

        # Label tag
        tag = f"{label} {score:.2f}"
        (tw, th), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(img, (x1, max(0, y1 - 20)), (x1 + tw + 6, max(20, y1)), (0, 0, 200), -1)
        cv2.putText(img, tag, (x1 + 3, max(15, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    dir_name = os.path.dirname(image_path)
    base_name, ext = os.path.splitext(os.path.basename(image_path))
    output_path = os.path.join(dir_name, f"{base_name}_detected{ext}")
    cv2.imwrite(output_path, img)
    print(f"\nAnnotated image saved to: {output_path}")

if __name__ == "__main__":
    main()
