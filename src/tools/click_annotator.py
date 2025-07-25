import cv2

class ImageClickAnnotatorCV2:
    def __init__(self, image_path: str):
        self.img = cv2.imread(image_path)
        self.clone = self.img.copy()
        self.points = []
        cv2.namedWindow("image")
        cv2.setMouseCallback("image", self.click_event)
        while True:
            cv2.imshow("image", self.img)
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or len(self.points) == 4:  # ESC or 4 clicks
                break
        cv2.destroyAllWindows()
        with open("border_points.txt", "w") as f:
            for x, y in self.points:
                f.write(f"{x},{y}\n")
        print("Points:", self.points)

    def click_event(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(self.points) < 4:
            self.points.append((x, y))
            cv2.circle(self.img, (x, y), 4, (0, 0, 255), -1)
            print((x, y))

if __name__ == "__main__":
    ImageClickAnnotatorCV2("/Users/sashanktirumala/Desktop/chess_vm.png")
