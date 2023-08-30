import cv2
import matplotlib.pyplot as plt
import insightface
import datetime
from insightface.app import FaceAnalysis
import requests

app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=0, det_size=(640, 640))
swapper = insightface.model_zoo.get_model(
    'inswapper_128.onnx', download=False, download_zip=False)


def faceswap(img1_fn, img2_fn, plot_after=True):
    '''
        faceswap(배경이미지주소, 얼굴이미지주소, 얼굴분석모델(app), 스왑모델(swapper))

        pip install insightface, images라는 이미지 담는 디렉토리 만들어주기
    '''

    img1 = cv2.imread(img1_fn)
    img2 = cv2.imread(img2_fn)

    faces = app.get(img1)
    face2 = app.get(img2)[0]
    print("number of faces: ", len(faces))

    img1_ = img1.copy()

    dn = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    fn = f'fs_{dn}.jpg'

    if plot_after:
        for face in faces:
            img1_ = swapper.get(img1_, face, face2, paste_back=True)

        # plt.imshow(img1_[:, :, ::-1])
        # plt.axis('off')
        # plt.show()
        cv2.imwrite(f'images/{fn}', img1_)
        print("saved a file successfully")

    with open(f'images/{fn}', 'rb') as openfile:
        # 유니티 포톤의 url
        # requests.post('http://localhost:5000/files/upload',
        #             files={"newfile": openfile})
        print("send file to unity successfully")


if __name__ == '__main__':
    # faceswap('배경이미지 주소', '얼굴 이미지 주소', app, swapper)
    faceswap('images/arrow6.jpg', 'images/ic1.jpg')
