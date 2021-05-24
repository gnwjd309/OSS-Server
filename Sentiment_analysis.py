try:
    import jpype
except:
    import jpype
from konlpy.tag import Kkma
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
import numpy as np
import re
import pandas as pd
import csv

def summary(_sentences, words):
    ## GraphMatrix
    tfidf = TfidfVectorizer()
    cnt_vec = CountVectorizer()
    sentence_graph = []

    # build_sent_graph
    tfidf_mat = tfidf.fit_transform(words).toarray()
    sentence_graph = np.dot(tfidf_mat, tfidf_mat.T)

    # build_words_graph
    data = cnt_vec.fit_transform(words).toarray()
    cnt_vec_mat = normalize(data, axis=0)
    vocab = cnt_vec.vocabulary_
    words_graph = np.dot(cnt_vec_mat.T, cnt_vec_mat)
    idx2word = {vocab[word]: word for word in vocab}

    ## Rank
    # sentence graph
    A = sentence_graph
    d = 0.85
    matrix_size = A.shape[0]

    for id in range(matrix_size):
        A[id, id] = 0  # diagonal 부분을 0으로
        link_sum = np.sum(A[:, id])  # A[:, id] = A[:][id]
        if link_sum != 0:
            A[:, id] /= link_sum
        A[:, id] *= -d
        A[id, id] = 1

    B = (1 - d) * np.ones((matrix_size, 1))
    ranks = np.linalg.solve(A, B)  # 연립방정식 Ax = b

    sentence_graph_idx = {idx: r[0] for idx, r in enumerate(ranks)}

    sorted_sentence_rank_idx = sorted(sentence_graph_idx, key=lambda k: sentence_graph_idx[k], reverse=True)

    # word graph
    A = words_graph
    d = 0.85
    matrix_size = A.shape[0]

    for id in range(matrix_size):
        A[id, id] = 0  # diagonal 부분을 0으로
        link_sum = np.sum(A[:, id])  # A[:, id] = A[:][id]
        if link_sum != 0:
            A[:, id] /= link_sum
        A[:, id] *= -d
        A[id, id] = 1

    B = (1 - d) * np.ones((matrix_size, 1))
    ranks = np.linalg.solve(A, B)  # 연립방정식 Ax = b

    words_graph_idx = {idx: r[0] for idx, r in enumerate(ranks)}

    sorted_words_rank_idx = sorted(words_graph_idx, key=lambda k: words_graph_idx[k], reverse=True)

    # summarize
    sent_num = 3
    summary = []
    index = []

    for idx in sorted_sentence_rank_idx[:sent_num]:
        index.append(idx)

    index.sort()
    for idx in index:
        summary.append(_sentences[idx])

    # keywords
    word_num = 10
    keywords = []
    index = []
    summarys = []

    for idx in sorted_words_rank_idx[:word_num]:
        index.append(idx)

    # index.sort()
    for idx in index:
        keywords.append(idx2word[idx])

    count = 0

    for row in summary:
        print(row)
        summarys.append(row)
        count = count + 1
        if (count > 3):
            break

    print('keywords :', keywords)
    return summarys, keywords


def text_processing(start, end, _sentences):
    table = dict()
    with open('polarity.csv', 'r', -1, 'utf-8') as polarity:
        next(polarity)

        for line in csv.reader(polarity):
            key = str()
            for word in line[0].split(';'):
                key += word.split('/')[0]
            table[key] = {'Neg': line[3], 'Neut': line[4], 'Pos': line[6]}

    columns = ['negative', 'neutral', 'positive']
    df = pd.DataFrame(columns=columns)

    file_stop_word = open('stop_words_file.txt', 'r', -1, 'utf-8')
    stop_word = file_stop_word.read()
    stop_word_list = []
    negative_list = []
    neutral_list = []
    positive_list = []
    for word in stop_word.split(','):
        if word not in stop_word_list:
            stop_word_list.append(word)
            file_stop_word.close()

    for i in range(start, end):
        words = str(_sentences)
        hangul = re.compile('[^ ㄱ-ㅣ가-힣]+')
        words = hangul.sub('', words)
        words_list = []
        for i in words:
            if i not in stop_word_list:
                words_list.append(i)

    negative = 0
    neutral = 0
    positive = 0

    for word in words_list:
        if word in table:
            negative += float(table[word]['Neg'])
            neutral += float(table[word]['Neut'])
            positive += float(table[word]['Pos'])

    negative_list.append(negative)
    neutral_list.append(neutral)
    positive_list.append(positive)

    df['negative'] = negative_list
    df['neutral'] = neutral_list
    df['positive'] = positive_list
    del negative_list,neutral_list,positive_list,negative,neutral,positive,words_list
    return df

def sentiment_analysis(_sentences):
    ds = text_processing(0,366, _sentences)
    ds == ds.values.max()
    ids, cols = np.where(ds == ds.values.max())
    list(zip(ids, cols))
    sen = [ds.columns[c] for c in cols]
    return sen


okt = Okt()
kkma = Kkma()


def data(category_sentence):
    _sentences = kkma.sentences(category_sentence)
    words = []

    for j in _sentences:
        word = okt.nouns(category_sentence)
        word_str = ' '.join(word)
        words.append(word_str)

    sentiment_result=sentiment_analysis(_sentences)
    summary_result,keywords=summary(_sentences, words)
    del words
    del word
    del _sentences
    del word_str
    return summary_result, keywords, sentiment_result