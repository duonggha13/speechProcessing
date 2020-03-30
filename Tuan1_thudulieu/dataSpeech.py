import os

import nltk.data
import sounddevice as sd
import soundfile as sf
import queue

topics = ['thoisu', 'gocnhin', 'thegioi', 'kinhdoanh', 'giaitri', 'thethao', 'phapluat', 'giaoduc', 'suckhoe', 'doisong', 'dulich', 'khoahoc', 'sohoa', 'xe', 'ykien', 'tamsu']

def readFile(filePathIn):
	fin = open(filePathIn)
	data = fin.read()
	fin.close()
	return data
def separateSentences(data):
	tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
	sentences = tokenizer.tokenize(data)
	return sentences

q = queue.Queue()
def callback(indata, frames, time, status):
	if status:
		print(status)
	q.put(indata.copy())

def recording(filename):
	try:
		with sf.SoundFile(filename, mode='x', samplerate=22000, channels=1) as file:
			with sd.InputStream(samplerate=22000, channels=1, callback=callback):
				print('Start recording: ' + filename)
				print('press Ctrl+C to next sentence')
				while True:
					file.write(q.get())
	except KeyboardInterrupt:
		print('Done recording!')
		print('-' * 100)


def main():
	for topic in topics:
		filePathIn = './in/' + topic + '.txt'
		sentences = separateSentences(readFile(filePathIn))

		textOutPath = './out/' + topic + '/index.txt'

		fout = open(textOutPath, "w")
		fout.write(sentences[0] + '\n')


		for sentence in sentences[1:]:
			print(sentence)
			namerecord = topic + str(sentences.index(sentence)) + '.wav'
			fout.write(namerecord + '\n')
			fout.write(sentence + '\n')
			recording(namerecord)
			wavOutPath = './out/' + topic + '/' + namerecord
			os.rename(namerecord, wavOutPath)
if __name__ == '__main__':
	main()