import nltk.data
import keyboard
import getch
import sounddevice as sd
import soundfile as sf
import time
import os


topics = ['thoisu', 'gocnhin', 'thegioi', 'kinhdoanh', 'giaitri', 'thethao', 'phapluat', 'giaoduc', 'suckhoe', 'doisong', 'dulich', 'khoahoc', 'sohoa', 'xe', 'ykien', 'tamsu']

def wait():
    getch.getch()

def sync_record(filename, duration, fs, channels):
    print('recording')
    myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=channels)
    sd.wait()
    sf.write(filename, myrecording, fs)
    print('done recording')

def main():
	tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
	
	for topic in topics:
		filePathIn = './in/' + topic +'.txt'
		fin = open(filePathIn)
		data = fin.read()
		fin.close()

		sentences = tokenizer.tokenize(data)

		filePathOut = './out/' + topic + '/description.txt'
		fout = open(filePathOut, "w")
		fout.write(sentences[0] + '\n')

		for sentence in sentences:
			if(sentences.index(sentence)==0):
				continue
			print(sentence)
			namerecord = topic + str(sentences.index(sentence)) + '.wav'
			fout.write(namerecord + '\n')
			fout.write(sentence + '\n')
			sync_record(namerecord, 10, 16000, 1)
			wait()
			sd.stop()
		fout.close()

if __name__ == '__main__':
	main()