import sys
import ast
import os
import gc# 内存管理模块
from tqdm import trange
from Bio.Seq import Seq
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
import multiprocessing # Step I : 导入模块
from multiprocessing import cpu_count#读取CPU核心数用于匹配线程数
import CentriVision.bez as bez
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')# 强制使用非交互式后端（交互式后端在GUI资源枯竭或满线程情况下报错）



class Dotplot():
	def __init__(self, options):
		self.workpath = os.getcwd()+'/'
		self.workpaths = './Dotplot/'
		self.fastapath = './fasta/'
		self.plotpath = './plot/'
		self.plot = 'False'
		self.temp = 'False'
		self.temppath = './temp/'
		self.pilpath = './PIL/'
		self.histpath = './hist/'
		self.hist = 'False'
		self.cpu = 16
		self.gap = -10
		self.windows = 4000
		self.minlength = 8
		self.konbai = 20
		self.poly = 'False'
		self.m = '0.3'
		# self.score_matrix = pd.read_excel(bez.get_scorefile())

		path = bez.get_path()
		font_path = os.path.join(path, 'example/arial.ttf')
		from matplotlib.font_manager import FontProperties
		self.font_prop = FontProperties(fname=font_path)

		bez_conf = bez.config()
		for k, v in bez_conf:# 
			setattr(self, str(k), v)
		for k, v in options:
			setattr(self, str(k), v)
			print(str(k), ' = ', v)
		self.cpu = int(self.cpu)
		self.windows = int(self.windows)
		self.gap = int(self.gap)
		self.minlength = int(self.minlength)
		self.konbai = int(self.konbai)
		self.m = float(self.m)
		if self.cpu > cpu_count():
			self.cpu = cpu_count()

	# def get_match_score(self,s1,s2,score_matrix):	#获取替换打分
	# 	# global  score_matrix
	# 	s = ['A','G','C','T'].index(s2)
	# 	score = score_matrix[s1][s]
	# 	return score

	def update_best_matrix(self,s1,s2,best_matrix,gap):
		job = len(s2)+1
		for i in range(len(s2)+1):
			p = int(((i+2)/job)*50)
			print("\r["+"*"*p+" "*(50-p)+"]  \033[0;31;42m"+str(i+1)+"\033[0m / "+str(job)+' -> update_matrix ',end="")
			for j in range(len(s1)+1):
				if i == 0 or j == 0 or i == j:
					best_matrix[i][j] = 0
				else:
					if s2[i-1] != s1[j-1] or s2[i-1] == 'N' or s1[j-1] == 'N':
						best_matrix[i][j] = 0
					else:
						match = 1
						if j >= 2 and i >= 2 and self.poly == 'True':# 舍弃单碱基重复
							if s2[i-2] == s1[j-2] and s2[i-1] == s2[i-2]:
								match = 0
						match_score = best_matrix[i-1][j-1]+match
						best_matrix[i][j] = match_score
		# print(best_matrix)
		return best_matrix

	def clear_matrix(self,s1,s2,data,gap,match,unmatch,name):
		cleardata = []
		repeat_dic = {}
		print('')
		job = len(data)
		length = len(s1)
		np_p =  np.zeros(shape= (job,job),dtype = int)
		for i in range(job):
			p = int(((i+1)/job)*50)
			print("\r["+"*"*p+" "*(50-p)+"]  \033[0;31;42m"+str(i+1)+"\033[0m / "+str(job)+ ' -> clear ',end="")
			for j in range(job):
				if data[-i][-j] >= self.minlength and np_p[-i][-j] == 0: #从后往前遍历，如果当前分数大于最小长度
					# print('score',data[-i][-j])
					l = data[-i][-j]
					cleardata.append(data[-i][-j])
					np_p[-i][-j] = data[-i][-j]
					x,y = i,j
					d = 0
					s1_,s2_ = s1[-i],s2[-j]
					while 1:
						note = data[-x][-y]
						note1 = data[-x-1][-y-1]
						note2 = data[-x-1][-y]
						note3 = data[-x][-y-1]
						# print('\n',note,note1,note2,note3,x,y)
						if -x-1 > -job and -y-1 > -job and note1 != 0 and (note == note1 + match or note == note1 + unmatch):
							np_p[-x-1][-y-1] = data[-x-1][-y-1]
							# print(s1[-x-1],s2[-y-1],data[-x-1][-y-1])
							s1_,s2_ = s1[-x-1]+s1_,s2[-y-1]+s2_
							x,y = -(-x-1),-(-y-1)
							d += 1
							continue
						else:
							break
							# exit()
					# print(s1_,s2_)
					if s1_ not in repeat_dic.keys():
						repeat_dic[s1_] = [length-i-l+1,length-j-l+1]# 输出的gff文件中的位置从0开始
					else:
						repeat_dic[s1_] += [length-i-l+1,length-j-l+1]# 输出的gff文件中的位置从0开始
						repeat_dic[s1_] = list(set(repeat_dic[s1_]))
		# print(repeat_dic)
		out_list = []
		all_repeat = []

		for key in repeat_dic.keys():
			all_repeat.append(len(repeat_dic[key]))
			s = '\t'.join([name,str(len(s1)),key,str(len(key)),str(len(repeat_dic[key])),'_'.join([str(i) for i in repeat_dic[key]])])
			out_list.append(s)

		# seed_number = len(repeat_dic)
		# means = sum(all_repeat)/seed_number

		f0 = open(self.workpaths+self.fastapath+self.outfile+'.repeat.index.txt','a')
		f0.write('\n'.join(out_list)+'\n')
		f0.close()


		if len(all_repeat) > 10:# 防止数据集为空
			from statistics import mode,median,mean,variance
			# 计算数组的众数
			mode_value = mode(all_repeat)
			# 计算数组的均值
			mean_value = mean(all_repeat)
			# 计算数组的中位数
			median_value = median(all_repeat)
			# 计算数组的方差
			variance_value = variance(all_repeat)
			max_count = max(all_repeat)
		else:
			mode_value,mean_value,median_value,variance_value,max_count = 0,0,0,0,0

		return np_p,len(data)-1,mode_value,mean_value,median_value,variance_value,max_count,cleardata


		# if len(cleardata) != 0:# 防止数据集为空
		# 	from statistics import mode,median,mean,variance
		# 	# 计算数组的众数
		# 	mode_value = mode(cleardata)
		# 	# 计算数组的均值
		# 	mean_value = mean(cleardata)
		# 	# 计算数组的中位数
		# 	median_value = median(cleardata)
		# 	# 计算数组的方差
		# 	variance_value = variance(cleardata)
		# else:
		# 	mode_value,mean_value,median_value,variance_value = 0,0,0,0

		# return np_p,len(data)-1,mode_value,mean_value,median_value,variance_value,cleardata

	def np2plot(self,s1,s2,best_matrix,gap,name):

		print('')
		np_p =  np.zeros(shape= (len(s2)+1,len(s1)+1),dtype = int)
		np_p[np_p==0] = 255
	
		x,y = [],[]
		job = len(s2)+1
		for i in range(len(s2)+1):
			p = int(((i+1)/job)*50)
			print("\r["+"*"*p+" "*(50-p)+"]  \033[0;31;42m"+str(i+1)+"\033[0m / "+str(job)+ ' -> drawing ',end="")
			for j in range(len(s1)+1):
				if best_matrix[i][j] > 0 or i == j:
					x.append(j)
					y.append(-i)
					np_p[i][j] = 0
		if self.plot == 'True':
			fig = plt.subplots(figsize = (12,12))
			plt.scatter(x, y,s=0.1,c='black', edgecolor='none')
			plt.xlim(0,job)
			plt.ylim(-job,0)
			# plt.axis('off')
			plt.savefig(self.workpaths+'./plot/'+name+'.png',dpi = 1000, bbox_inches='tight')	
			# plt.show()
			# 清除画布
			plt.close()

		plt.imshow(np.array(np_p), cmap='gray')
		plt.savefig(self.workpaths+'./PIL/'+name+'.png', dpi = 1000, bbox_inches = 'tight')# 存储图片
		plt.close()
		# print('\n')

	def condense_array(self,original_array, target_length=100):
		old_length = len(original_array)
		new_original_array = []
		for i in original_array:
			new_original_array = new_original_array + [i]*target_length
		condensed_array = []
		for i in range(target_length):
			condensed_array.append(sum(new_original_array[i*old_length:(i+1)*old_length])/float(old_length))
		return np.array(condensed_array)

	def read_best_matrix(self,matrix):
		matrix = np.int64(matrix>0)
		# 对每行求和
		row_sums = np.sum(matrix, axis=1)[1:]#行
		col_sums = np.sum(matrix, axis=0)[1:]#列
		# 将数组浓缩为长度为100的数组
		row_sums = list(self.condense_array(row_sums))
		col_sums = list(self.condense_array(col_sums))
		matrix_s = row_sums+col_sums
		# del matrix,row_sums,col_sums
		return [float(i)/(len(matrix)-1) for i in matrix_s]

	def AMPD1(self,data,threshold):
		"""
		实现AMPD算法
		:param data: 1-D numpy.ndarray 
		:return: 波峰所在索引值的列表
		"""
		p_data = np.zeros_like(data, dtype=np.int32)
		count = data.shape[0]
		arr_rowsum = []
		for k in range(1, count // 2 + 1):
			row_sum = 0
			for i in range(k, count - k):
				if data[i] > data[i - k] and data[i] > data[i + k]:
					row_sum -= 1
			arr_rowsum.append(row_sum)
		min_index = np.argmin(arr_rowsum)
		max_window_length = min_index
		for k in range(1, max_window_length + 1):
			for i in range(k, count - k):
				if data[i] > data[i - k] and data[i] > data[i + k]:
					p_data[i] += 1
		return np.where(p_data == max_window_length)[0]

	def AMPD(self, data, threshold):
		"""
		实现AMPD算法，并通过阈值过滤小波动
		:param data: 1-D numpy.ndarray 
		:param threshold: 过滤波峰的振幅阈值，默认为0（即不过滤）
		:return: 波峰所在索引值的列表
		"""
		p_data = np.zeros_like(data, dtype=np.int32)
		count = data.shape[0]
		arr_rowsum = []
		
		# 计算行和
		for k in range(1, count // 2 + 1):
			row_sum = 0
			for i in range(k, count - k):
				if data[i] > data[i - k] and data[i] > data[i + k]:
					row_sum -= 1
			arr_rowsum.append(row_sum)
		
		min_index = np.argmin(arr_rowsum)
		max_window_length = min_index
		
		# 统计局部最大值
		for k in range(1, max_window_length + 1):
			for i in range(k, count - k):
				if data[i] > data[i - k] and data[i] > data[i + k]:
					p_data[i] += 1
		
		# 获取波峰索引
		peak_indices = np.where(p_data == max_window_length)[0]
		
		# 通过阈值过滤小波峰
		if threshold > 0:
			peak_indices = [i for i in peak_indices if data[i] > threshold]
		
		return np.array(peak_indices)



	def find_best_split(self,arro):
		# 对数组进行排序
		arr = sorted(arro)
		# 计算数组长度
		n = len(arr)

		# 初始化变量
		min_difference = float('inf')
		best_split_index = 0
	
		# 初始化前缀和数组
		prefix_sum = np.cumsum(arr)
		
		# 遍历每一个可能的分割点
		for i in range(1, n):
			# 计算前半部分和后半部分的平均值
			left_sum = prefix_sum[i - 1]
			right_sum = prefix_sum[-1] - prefix_sum[i - 1]
			
			left_avg = left_sum / i
			right_avg = right_sum / (n - i)
			
			# 计算两个部分的平均值的差异
			difference = abs(left_avg - right_avg)
			
			# 更新最小差异和最佳分割点
			if difference < min_difference:
				min_difference = difference
				best_split_index = i
		
		# 根据最佳分割点分割数组
		left_part = arr[:best_split_index]
		right_part = arr[best_split_index:]
		
		return left_part, right_part

	def start(self,s1,s2,name):
		best_matrix = np.zeros(shape= (len(s2)+1,len(s1)+1),dtype = int)	#初始化得分矩阵
		best_matrix = self.update_best_matrix(s1,s2,best_matrix,self.gap)
		gc.collect()
		if self.temp == 'True':
			np.savetxt(self.workpaths+'./temp/'+name+'.csv',best_matrix,fmt='%d',delimiter='\t')
		best_matrix1,length,mode_value1,mean_value1,median_value1,variance_value1,max_count,cleardata = self.clear_matrix(s1,s2,best_matrix,self.gap,1,0,name)
		gc.collect()
		matrix_s = self.read_best_matrix(best_matrix1)

		self.np2plot(s1,s2,best_matrix1,self.gap,name)

		for i in range(len(best_matrix1)):
			best_matrix1[i][i] = 1

		print('\t'+name)

		matrix0 = np.where(np.array(best_matrix1) >= 1, 1, 0)

		if self.temp == 'True':
			np.savetxt(self.workpaths+'./temp/'+name+'.one.csv',matrix0,fmt='%d',delimiter='\t')

		matrix0[matrix0==0] = 255

		matrix_new = []
		for y in best_matrix1:
			arr = np.array(y)
			# print(arr)
			if arr.sum() == 0:
				continue
			# 找到第一个非零数字的位置
			nonzero_indices = np.where(arr != 0)  # 获取非零索引
			first_nonzero_index = nonzero_indices[0][0]  # 获取第一个非零索引
			if first_nonzero_index != 0:
				y0 = list(y)[first_nonzero_index:] + list(y)[:first_nonzero_index]
			else:
				y0 = list(y)
			matrix_new.append(y0)

		matrix = np.where(np.array(matrix_new) >= 1, 1, 0)# 冗余的一次数据清洗

		if self.temp == 'True':
			np.savetxt(self.workpaths+'./temp/'+name+'.phase.csv',matrix,fmt='%d',delimiter='\t')

		matrix_p = matrix.copy()
		matrix_p[matrix_p==0] = 255

		col_sums = np.sum(matrix, axis=0)[1:]#列
		x = [i for i in range(len(col_sums))]
		plt.imshow(matrix0, cmap='gray')
		plt.plot(x, col_sums, alpha=0.6, label='Phase synchronization')
		px = self.AMPD(col_sums,len(s1)*0.1)

		if len(px) == 0:
			mode_value = 0
			number = 0
			px_c = 0
		else:
			peakx,peaky = px, col_sums[px]
			maxpeak = max(col_sums[px])
			peakx1,peaky1 = [],[]
			for i in range(len(peakx)):
				if peaky[i]<maxpeak*self.m:
					continue
				else:
					peakx1.append(peakx[i])
					peaky1.append(peaky[i])
			plt.scatter(px, col_sums[px], color="black",s=1, label='AMPD', alpha=0.8)
			plt.scatter(peakx1, peaky1, color="red",marker='x',s=10, label='AMPD-F', alpha=0.8)

			if len(peakx1) > 10:
				y_array = np.array(peaky1)
				top_indices = np.argsort(y_array)[-5:]
				top_x = [peakx1[i] for i in top_indices]
				top_y = [peaky1[i] for i in top_indices]
				px_c = sum(top_y)/len(top_y)
			else:
				top_x = peakx1
				top_y = peaky1
				px_c = sum(top_y)/len(top_y)
			for x,y in zip(top_x,top_y):
				plt.text(x, y, str(x)+'_'+str(y), fontsize=12, fontproperties=self.font_prop, verticalalignment='bottom',horizontalalignment='center', rotation=90)

			# 使用嵌套循环计算差值
			differences = []
			for i in range(len(peakx1)):
				if i+2 >= len(peakx1):
					continue
				for j in range(i + 1, i + 2):
					seedlength = abs(peakx1[i] - peakx1[j])
					if seedlength >= self.minlength:
						differences.append(seedlength)  # 计算绝对差值

			if len(differences) >= 3:
				from statistics import mode,mean
				# 计算数组的众数
				mode_value = mode(differences)
				# 计算数组的均值
				mean_value = mean(differences)
				number = differences.count(mode_value)
				for i in range(1,int(mode_value*0.1)+1):
					number += differences.count(mode_value+i)
					number += differences.count(mode_value-i)
				number += 2
				# print(name,'众数:',mode_value,differences.count(mode_value)+2,number)
			else:
				mode_value = 0
				number = 0

		# plt.legend()  # 显示图例
		plt.yticks([])
		plt.savefig(self.workpaths+'./hist/'+name+'.png', dpi = 600, bbox_inches = 'tight')# 存储图片
		plt.close()

		gc.collect()
		GC = (s1.count('G')+s1.count('C'))/len(s1)
		seq_mode = mode_value
		seq0 = s1[:seq_mode]
		return [length,GC,number,mode_value1,mean_value1,median_value1,variance_value1,max_count,px_c,seq_mode]+matrix_s+[seq0]


	def run(self):
		pool = multiprocessing.Pool(processes = self.cpu)
		genome = SeqIO.to_dict(SeqIO.parse(self.genome_file, "fasta"))
		if not os.path.exists(self.workpaths):
			# 如果文件夹不存在，则创建文件夹
			os.makedirs(self.workpaths)
		if not os.path.exists(self.workpaths+self.fastapath):
			os.makedirs(self.workpaths+self.fastapath)
		if not os.path.exists(self.workpaths+self.plotpath) and self.plot == 'True':
			os.makedirs(self.workpaths+self.plotpath)

		if not os.path.exists(self.workpaths+self.temppath) and self.temp == 'True':
			os.makedirs(self.workpaths+self.temppath)

		if not os.path.exists(self.workpaths+self.pilpath):
			os.makedirs(self.workpaths+self.pilpath)
		if not os.path.exists(self.workpaths+self.histpath):
			os.makedirs(self.workpaths+self.histpath)

		# if not os.path.exists(self.workpaths+'./plotcsv/'):
		# 	os.makedirs(self.workpaths+'./plotcsv/')
		# if not os.path.exists(self.workpaths+'./clearcsv/'):
		# 	os.makedirs(self.workpaths+'./clearcsv/')
		f0 = open(self.workpaths+self.fastapath+self.outfile+'.repeat.index.txt','w')
		f0.write('\t'.join(['split_name','split_length','seq','length','number','index(Index starts from 0)'])+'\n')
		f0.close()
		f = open(self.workpaths+self.fastapath+self.outfile+'.split.fasta','w')
		f1 = open(self.workpaths+self.fastapath+self.outfile+'.split.gff','w')
		results = {}
		for key in genome.keys():
			s = str(genome[key].seq).upper()
			job = int(len(s)/self.windows)
			if job == 0:
				job = 1
			for i in range(job):
				if i == job - 1:
					s0 = s[self.windows*i:]
				else:
					s0 = s[self.windows*i:self.windows*(i+1)]
				s1,s2 = s0,s0
				if 'N' in s1:
					continue
				name = key+'_s'+str(i)
				f.write('>'+name+'\n'+s1+'\n')		
				f1.write('\t'.join([key,name,str(self.windows*i),str(self.windows*(i+1))])+'\n')	
				# if os.path.exists(self.pilpath+name+'.png') and os.path.exists(self.plotpath+name+'.png'):
				# 	continue
				dic = {}
				dic['gff'] = [key,'dotplot',name,str(self.windows*i+1),'.']
				dic['value'] = pool.apply_async(self.start, (s1,s2,name),  error_callback=bez.print_error)
				
				results[name] = dic
		pool.close() # Step IV : 准备结束
		pool.join() # Step IV : 完全结束
		f.close()
		f1.close()
		# print("")
		print("********************输出********************")

		names = list(results.keys())
		maker = ['length','GC','number','mode_value','mean_value','median_value','variance_value','max_count','AMPD_top','seed_l']+['M'+str(i) for i in range(1,201)]+['seed']
		f = open(self.workpath+self.outfile,'w')
		f.write('\t'.join(['chr','dotplot','name','start','end']+maker)+'\n')
		value = [[] for _ in range(len(maker))]
		for j in range(len(names)):
			name = names[j]
			lt = results[name]['value'].get()
			for i in range(len(lt)):
				value[i].append(lt[i])
			lt = results[name]['gff'] + lt
			f.write('\t'.join([str(s) for s in lt])+'\n')
		f.close()


