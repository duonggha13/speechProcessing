import librosa
import numpy as np
import os
import math
from sklearn.cluster import KMeans
import hmmlearn.hmm
import operator
import pickle
from pprint import pprint


def get_mfcc(file_path):
    y, sr = librosa.load(file_path)  # read .wav file
    hop_length = math.floor(sr*0.010)  # 10ms hop
    win_length = math.floor(sr*0.025)  # 25ms frame
    # mfcc is 12 x T matrix
    mfcc = librosa.feature.mfcc(
        y, sr, n_mfcc=12, n_fft=1024,
        hop_length=hop_length, win_length=win_length)
    # substract mean from mfcc --> normalize mfcc
    mfcc = mfcc - np.mean(mfcc, axis=1).reshape((-1, 1))
    # delta feature 1st order and 2nd order
    delta1 = librosa.feature.delta(mfcc, order=1)
    delta2 = librosa.feature.delta(mfcc, order=2)
    # X is 36 x T
    X = np.concatenate([mfcc, delta1, delta2], axis=0)  # O^r
    # return T x 36 (transpose of X)
    return X.T  # hmmlearn use T x N matrix


def get_class_data(data_dir):
    files = os.listdir(data_dir)
    mfcc = [get_mfcc(os.path.join(data_dir, f))
                     for f in files if f.endswith(".wav")]
    return mfcc


def clustering(X, n_clusters=10):
    kmeans = KMeans(n_clusters=n_clusters, n_init=50,
                    random_state=0, verbose=0)
    kmeans.fit(X)
    print("centers", kmeans.cluster_centers_.shape)
    return kmeans
def get_start_and_trans_matrix(name):
    state_map = {}
    state_map['benhnhan'] = 22
    state_map['vietnam'] = 22
    state_map['cach'] = 11
    state_map['nguoi'] = 11
    state_map['phai'] = 11
    state_map['test_benhnhan'] = 22
    state_map['test_vietnam'] = 22
    state_map['test_cach'] = 11
    state_map['test_nguoi'] = 11
    state_map['test_phai'] = 11

    n_state = state_map[name]
    # n_state = 6

    # Create startprob_prior
    startprob_prior = np.array([1.0])
    for i in range(1, n_state):
        startprob_prior = np.append(startprob_prior, [0.0])

    # Create transmat_prior
    transmat_prior = np.array([])
    for x in range(0, n_state):
        a = np.array([])
        for y in range(0, n_state):
            prob = 0.0
            if y == x+1:
                prob = 0.6
            if y == x+2:
                prob = 0.4
            if x == n_state-1 == y:
                prob = 1.0
            a = np.append(a, [prob])
        if x != 0:
            transmat_prior = np.vstack([transmat_prior, a])
        else:
            transmat_prior = a

    return startprob_prior, transmat_prior

if __name__ == "__main__":
    class_names = ["song", "thay", "test_song", "test_thay", "thoi_gian",  "test_thoi_gian", "y_te", "test_y_te", "truoc", "test_truoc"]
    dataset = {}
    for cname in class_names:
        print(f"Load {cname} dataset")
        dataset[cname] = get_class_data(os.path.join("data", cname))

    models = {}
    for cname in class_names:
        startprob_prior, transmat_prior = get_start_and_trans_matrix(cname)
        hmm = hmmlearn.hmm.GMMHMM(
            n_mix=2, n_iter=1000, verbose=True,
            n_components = len(startprob_prior),
            params = 'mctw',
            init_params = 'mct',
            startprob_prior = startprob_prior,
            transmat_prior = transmat_prior, 
        )
        if cname[:4] != 'test':
            X = np.concatenate(dataset[cname])
            lengths = list([len(x) for x in dataset[cname]])
            print("training class", cname)
            print(X.shape, lengths, len(lengths))
            hmm.fit(X)
            models[cname] = hmm

    print("Training done")

    # Export model weight
    for cname in class_names:
        if cname[:4] != 'test':
            model = models[cname]
            outfile = open(cname + '.pkl', 'wb')
            pickle.dump(model, outfile)
            outfile.close()

    print("Testing")
        for true_cname in to_test:
        correct = 0
        failed = 0
        real_name = true_cname.split('_')[-1]

        for O in dataset[true_cname]:
            score = {cname : model.score(O, [len(O)]) for cname, model in models.items() if cname[:4] != 'test' }

            match = True
            for key in score:
                if key != real_name and score[key] > score[real_name]:
                    match = False
            if match:
                correct += 1
            else:
                failed += 1
            # print(real_name, score)

        acc = correct/(correct+failed)
        print(real_name + " : " + str(acc))
