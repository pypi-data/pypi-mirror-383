def reduce_frame_rate(input_path, output_path, desired_frame_rate):
    cap = cv2.VideoCapture(input_path)
    
    # 获取原始视频的帧率
    original_frame_rate = cap.get(cv2.CAP_PROP_FPS)
    # 计算每隔多少帧保留一帧，以达到目标帧率
    frame_skip_factor = int(original_frame_rate / desired_frame_rate)
    # 读取第一帧
    ret, frame = cap.read()
    # 打开输出视频文件
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, desired_frame_rate, (frame.shape[1], frame.shape[0]))
    frame_count = 0

    while ret:
        if frame_count % frame_skip_factor == 0:
            # 写入帧到输出视频文件
            out.write(frame)

        # 读取下一帧
        ret, frame = cap.read()
        frame_count += 1
    
    # 释放资源
    cap.release()
    out.release()
    
    
reduce_frame_rate("./video.mp4", "./output_video.mp4", 3)

########################################################################

def crop_pixel_region(input_path, output_path, x, y, width, height):
    cap = cv2.VideoCapture(input_path)

    original_frame_rate = cap.get(cv2.CAP_PROP_FPS)
    # 设置 VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, original_frame_rate, (width, height))

    # 读取并写入裁剪的帧
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cropped_region = frame[y:y+height, x:x+width]
        out.write(cropped_region)

    # 释放资源
    cap.release()
    out.release()

x, y, width, height = 700, 150, 700, 500  # 以像素为单位的裁剪区域
crop_pixel_region( "./video.mp4", "像素裁剪.mp4", x, y, width, height)
###########################################################################
def denoise_video(input_path, output_path, strength=10):
    cap = cv2.VideoCapture(input_path)
    original_frame_rate = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, original_frame_rate, (int(cap.get(3)), int(cap.get(4))))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 使用中值滤波进行降噪
        denoised_frame = cv2.medianBlur(frame, strength)
        out.write(denoised_frame)

    cap.release()
    out.release()

denoise_video("./video.mp4", "视频降噪.mp4", 5)
#################################################################################
def concatenate_videos(video_paths, output_path):
    videos = [cv2.VideoCapture(path) for path in video_paths]

    # 获取原始视频的帧率、宽度和高度
    original_frame_rate = videos[0].get(cv2.CAP_PROP_FPS)
    width = int(videos[0].get(3))
    height = int(videos[0].get(4))

    # 设置 VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, original_frame_rate, (width, height))

    for video in videos:
        while True:
            ret, frame = video.read()
            if not ret:
                break
            out.write(frame)

    # 释放资源
    for video in videos:
        video.release()
    out.release()
    
concatenate_videos(["./视频降噪.mp4", "./像素裁剪.mp4"],"视频合成.mp4")
###############################################################################
#定义函数创建停用词列表
def stopwordslist(filepath):   
    stopword = [line.strip() for line in open(filepath, 'r').readlines()]    #以行的形式读取停用词表，同时转换为列表
    return stopword

#########################################################################
def cutsentences(sentences, filepath):     #定义函数实现分词
    print('原句子为：'+ sentences)
    cutsentence = jieba.lcut(sentences.strip())     #精确模式
    print ('\n'+'分词后：'+ "/ ".join(cutsentence)) 
    stopwords = stopwordslist(filepath)     # 这里加载停用词的路径
    lastsentences = ''
    for word in cutsentence:     #for循环遍历分词后的每个词语
        if word not in stopwords:     #判断分词后的词语是否在停用词表内
            if word != '\t':
                lastsentences += word
                lastsentences += "/ "
    print('\n'+'去除停用词后：'+ lastsentences) 


##################################################################################

filepath= './data/stopwords_cn.txt'  
sentences = '万里长城是中国古代劳动人民血汗的结晶和中国古代文化的象征和中华民族的骄傲'
cutsentences(sentences, filepath)
####################################################################################

# 引入词性标注接口
import jieba.posseg as psg

re_internal = re.compile("([\u4E00-\u9FD5a-zA-Z0-9+#&\. ]+)")

text = "今天我参加云南的人工智能大赛"
#词性标注
seg = psg.cut(text)
#将词性标注结果打印出来
for ele in seg:
    print(ele)
#################################################################
# 读取文章的函数
def get_content(content_path):
    with open(content_path, 'r', encoding="utf-8", errors="ignore") as f:
        content = ''
        for i in f:
            i = i.strip()
            content += i
    return content

# 提取topK个高频词的函数
# TF:计算某个词在文章中出现的总次数
def get_TF(k,words):
    tf_dic = {}
    for i in words:
        tf_dic[i] = tf_dic.get(i, 0)+1
    return sorted(tf_dic.items(), key=lambda x: x[1], reverse=True)[:k]
 
#获取停用词
def stop_words(path):
    with open(path) as f:
        return [l.strip() for l in f]

#cut函数,path是你的停用词表所放的位置
def cut(content,path):
    split_words = [x for x in jieba.cut(content) if x not in stop_words(path)]
    return split_words 


##################################################################################################
files ="./data/TFdoc.txt"
corpus = get_content(files)
stopfile = "./data/stopwords.txt"
split_words = cut(corpus, stopfile)
print("top(k)个词为：" + str(get_TF(10, split_words)))