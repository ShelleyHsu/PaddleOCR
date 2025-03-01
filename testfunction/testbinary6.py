from paddleocr import PaddleOCR, draw_ocr
from pdf2image import convert_from_path
import os, cv2, numpy as np
import logging
import datetime
# Paddleocr supports Chinese, English, French, German, Korean and Japanese.
# You can set the parameter `lang` as `ch`, `en`, `french`, `german`, `korean`, `japan`
# to switch the language model in order.

pdf_folder = '../pdf/'
img_folder = '../img'
pdfoutputimg_folder_all = '../pdftoimg_all'
pdfoutputimg_folder_cover = '../pdftoimg_cover'
pdfoutputimg_folder_note = '../pdftoimg_note'
pdfoutputimg_folder_main = '../pdftoimg_main'
pdfoutputimg_folder_appendix = '../pdftoimg_appendix'
outputfile_folder = '../outputfile'
outputlog_folder = '../outputlog'
outputimg_folder = '../outputimg'
testpdf_folder = '../testpdfimg'
test_folder = '../testoutput'

for root, dirs, files in os.walk(pdf_folder):
    # do pdf to image
    for filename in files:
        if filename.endswith('.pdf'):
            file_path = os.path.join(root, filename)
            pages = convert_from_path(file_path,
                                    dpi=300,
                                    grayscale = True
                                    )
            # 保存圖像
            for i, page in enumerate(pages):
                # print(filename+" page"+str(i)+" w:"+str(page.size[0]))#PDF頁面的寬度
                # print(filename+" page"+str(i)+" h:"+str(page.size[1]))#PDF頁面的高度
                # output_path = os.path.join(pdfoutputimg_folder_all, f'{filename}_page_{i+1}.jpg')

                filename = os.path.splitext(filename)[0]
                # 依據頁面寬進行文本分類，寬<1000為note、2000<寬<4000為正文、寬>4000為附錄
                if page.size[0] < 2000:
                    output_path = os.path.join(testpdf_folder, f'{filename}_page_{i+1}_note.jpg')
                    page.save(output_path, 'JPEG')
                elif page.size[0] > 2000 and page.size[0] < 2400 :
                    output_path = os.path.join(testpdf_folder, f'{filename}_page_{i+1}_main.jpg')
                    page.save(output_path, 'JPEG')
                if page.size[0] > 2400 and page.size[0] < 3000 :
                    output_path = os.path.join(testpdf_folder, f'{filename}_page_{i+1}_cover.jpg')
                    page.save(output_path, 'JPEG')
                else:
                    output_path = os.path.join(testpdf_folder, f'{filename}_page_{i+1}.jpg')
                    page.save(output_path, 'JPEG')

# do ocr (stage1以笨文為主)
for filename in os.listdir(testpdf_folder):
    # print(filename)
    # print(img_folder+'/'+filename)

    ocr = PaddleOCR(use_angle_cls=True, lang='ch')#, rec_algorithm = 'chinese_cht') # need to run only once to download and load model into memory
    img_path = testpdf_folder+'/'+filename #'PaddleOCR/doc/imgs_en/img_12.jpg'
    # img_path = '../img/4-1.jpeg'

    # cv2.imread(img_path)
    # cv_img = cv2.cvtColor(np.asarray(img_path), cv2.COLOR_RGB2BGR)
    # gray_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    # ret, bin_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    #prepare output ocr result 
    result = ocr.ocr(img_path, cls=True)
    # 去掉副檔名
    filename = os.path.splitext(filename)[0]

    # draw result
    from PIL import Image
    result = result[0]
    image = Image.open(img_path).convert('RGB')
    boxes = [line[0] for line in result]
    print('---------------------------')
    # print(boxes)
    txts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]
    #im_show = draw_ocr(image, boxes, txts, scores, font_path='../PaddleOCR/doc/fonts/simfang.ttf')
    im_show = draw_ocr(image, boxes, txts, scores, font_path='../doc/fonts/chinese_cht.ttf')
    im_show = Image.fromarray(im_show)
    im_show.save(os.path.join(test_folder, f'{filename}_result_6.jpg'))


    # save to file
    righttop_location = [topright[2] for topright in boxes]
    # right to left order [right][top]
    righttop_order = [sorted(righttop_location,reverse=True)]

    # 搭配 with 寫入檔案
    output_path = os.path.join(test_folder, f'{filename}_6.txt')
    with open(output_path, 'w') as f:
        # get each box righttop(x, y)
        for righttop in righttop_order[0]:
            for line in result:
                # print(righttop)
                
                # check if match the righttop(x, y)
                if line[0][2] == righttop:
                    # write file
                    f.write(line[1][0]+'\n')
                    break
            else:
                continue