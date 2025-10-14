import requests
import argparse
import gxl_ai_utils

# url和端口携程自己的
flask_url = 'http://127.0.0.1:5012/predict'


def predict_result(image_path):
    #啥方法都行
    image = open(image_path, 'rb').read()
    payload = {'gxl_img': image}
    #request发给server.
    r = requests.post(flask_url, files=payload).json()

    # 成功的话在返回.
    if r['success']:
        # 输出结果.
        for (i, result) in enumerate(r['predictions']):
            print('{}. {}: {:.4f}'.format(i + 1, result['label'],
                                          result['probability']))
    # 失败了就打印.
    else:
        print('Request failed')


if __name__ == '__main__':
    data_path = gxl_ai_utils.AiConstant.DATA_PATH
    parser = argparse.ArgumentParser(description='Classification demo')
    parser.add_argument('--file', default=data_path+'/flower_data/train_filelist/image_06998.jpg', type=str, help='test_gxl_ai_utils image file')

    args = parser.parse_args()
    predict_result(args.file)
