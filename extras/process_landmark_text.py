# This file is used for preprocessing the text-video landmark sequence 
# The processed sequence is then used for training the text2face generation network
 
from glob import glob
from pydub import AudioSegment 
import os
import threading
from tqdm import tqdm
import random
import time
from concurrent.futures import ThreadPoolExecutor
from moviepy.editor import *
import numpy as np
import unicodedata
import re

def extract_transcript(id_text_file):
	text_file, j = id_text_file
	audio_file = text_file.replace('txt', 'wav')

	transcript_dir = 'transcript_files'
	os.makedirs(transcript_dir, exist_ok=True)

	failed_files = os.path.join(transcript_dir, 'failed_transcripts.txt')
	tts_mapping = os.path.join(transcript_dir, 'tts_vlog.txt')

	# check for the existence of the wav file
	if not os.path.isfile(audio_file):
		# print(f'Failed adding transcript for file : {text_file}')
		with open(failed_files, 'a') as f:
			f.write(text_file + '\n')
		return

	# iterate through the lines to get the transcript
	with open(text_file, 'r') as f:
		line = f.read().splitlines()

	# print(line)
	
	text = line[0].split("{'text': ")[1].split(", 'start'")[0].strip('\"\'')
	# normalize the string and replace the \n characters with ' ' character
	normalized_text = unicodedata.normalize("NFKD", text).replace('\n', ' ')

	if '[' in text or ']' in normalized_text:
		# print(f'Failed adding transcript for file : {text_file}')
		with open(failed_files, 'a') as f:
			f.write(text_file + '\t' + normalized_text + '\n')
		return

	# Finally create mapping between audio file and transcript
	with open(tts_mapping, 'a') as f:
		f.write(audio_file + '|' + normalized_text + '\n')


# remove audio files greater than audio_threshold duration, audio_threshold is specified in seconds
def filter_audio_duration(filename, audio_threshold=15):
	with open(filename, 'r') as f:
		files = f.read().splitlines()

	files_filtered = dict()
	added_files = list()
	for file in files:
		audio_file = file.split('|')[0]
		audio = AudioSegment.from_file(audio_file)
		if audio.duration_seconds > audio_threshold:
			# files_filtered += 1
			files_filtered[audio_file] = audio.duration_seconds
			continue 
		else:
			added_files.append(file)
	
	# write the file to location 
	print(f'Files ignored : {len(files_filtered)}, files to add : {len(added_files)}')
	new_filename = os.path.join('/'.join(filename.split('/')[:-1]), os.path.basename(filename).split('.')[0] + '_updated.txt')
	with open(new_filename, 'w') as f:
		for file in added_files:
			f.write(file + '\n')

	print(f'All files ignored')
	print(files_filtered)

# code used to normalize the text transcripts 
# removes all unnecessary characters, replaces multiple spaces with a single space, trims leading and training space characters
def normalize_text(filename):
	with open(filename, 'r') as f:
		lines = f.read().splitlines()

	new_lines = list()
	for line in lines:
		line = line.replace('\\xa0', ' ').replace('\\n', ' ').replace('\\\'', '\'')
		# more than one spaces are replaced with a single space, leading and trailing spaces are stripped
		line = re.sub(' +', ' ', line).strip()
		new_lines.append(line)

	# write the new_lines to the modified tts file 
	new_tts_path = os.path.join('/'.join(filename.split('/')[:-1]), os.path.basename(filename).split('.')[0] + '_normalized.txt')
	with open(new_tts_path, 'w') as f:
		for line in new_lines:
			f.write(line + '\n')
		
	print(f'Lines written successfully: {len(new_lines)}')

def normalize_text_landmark(filename):
	with open(filename, 'r') as f:
		lines = f.read().splitlines()

	new_lines = list()
	for line in lines:
		text, video_landmark_path = line.split('|')[0], line.split('|')[1]
		text = text.replace('\\xa0', ' ').replace('\\n', ' ').replace('\\\'', '\'')
		text = re.sub(' +', ' ', text).strip()
		new_lines.append(text + '|' + video_landmark_path)
	
	# write the new file to path 
	modified_filepath = os.path.join('/'.join(filename.split('/')[:-1]), os.path.basename(filename).split('.')[0] + '_normalized.txt')
	with open(modified_filepath, 'w') as f:
		for line in new_lines:
			f.write(line + '\n')

	print(f'File normalized successfully : {len(new_lines)} at location : {modified_filepath}')

if __name__ == '__main__':
	thread_limit = 5
	video_files = glob('SpeakerData/videos/*/*/*.mp4')
	transcript_files = glob('SpeakerData/videos/*/*/????.txt')

	# jobs = [(vfile, i%thread_limit) for i, vfile in enumerate(video_files)]
	# p = ThreadPoolExecutor(thread_limit)
	# futures = [p.submit(generate_audio_from_video, j) for j in jobs]
	# _ = [r.result() for r in tqdm(as_completed(futures), total=len(futures))]

	# for transcript_file in tqdm(transcript_files):
	# 	extract_transcript((transcript_file, 0))

	# filter audio files based on audio duration 
	# filename = 'filelists/vlog_train.txt'
	# filter_audio_duration(filename)

	# normalize text by processing text transcript 
	# filename = 'filelists/vlog_val.txt'
	filename = 'vlog_train_text_landmarks.txt'
	# normalize the text file with the sequence of text|video_landmark_path
	normalize_text_landmark(filename)
	# normalize_text(filename)

	# filename = 'SpeakerData/videos/AnfisaNava/1Kd3JiQBxXQ/0192.txt'
	# extract_transcript((filename, 0))

	# filename = 'SpeakerData/videos/AnfisaNava/1Kd3JiQBxXQ/0191.mp4'
	# generate_audio_from_video((filename, 0))

	# with ThreadPoolExecutor(thread_limit) as e:
	# 	results = e.map(sleep_job, ((thread_id, folder) for thread_id, folder in enumerate(folder_list)))