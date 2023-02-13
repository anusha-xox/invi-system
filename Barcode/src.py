from pyzbar import pyzbar
import cv2


class Barcode:
    def __init__(self):
        pass

    def draw_barcode(self, decoded, image):
        image = cv2.rectangle(image, (decoded.rect.left, decoded.rect.top),
                              (decoded.rect.left + decoded.rect.width, decoded.rect.top + decoded.rect.height),
                              color=(0, 255, 0),
                              thickness=5)
        return image

    def decode(self, image):
        # decodes all barcodes from an image
        decoded_objects = pyzbar.decode(image)
        for obj in decoded_objects:
            # draw the barcode
            print("detected barcode:", obj)
            image = self.draw_barcode(obj, image)
            # print barcode type & data
            print("Type:", obj.type)
            print("Data:", obj.data)
            print()

        return image

    # In[5]:

    def initiate(self):
        from glob import glob
        cam = cv2.VideoCapture(0)
        ret, img = cam.read()
        barcodes = img
        while ret:
            # load the image to opencv
            ret, img = cam.read()
            if cv2.waitKey(1) == ord('q'):
                img = self.decode(img)
            # show the image
            cv2.imshow("img", img)
            if cv2.waitKey(1) & 0xFF == 27:
                break
        cam.release()
        cv2.destroyAllWindows()


b = Barcode()
b.initiate()