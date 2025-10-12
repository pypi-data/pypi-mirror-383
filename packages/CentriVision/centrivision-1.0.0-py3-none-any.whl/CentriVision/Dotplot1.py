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
class Dotplot():
	def __init__(self, options):
		self.workpath = os.getcwd()+'/'
		self.workpaths = './Dotplot/'
		self.fastapath = './fasta/'
		self.plotpath = './plot/'
		self.plot = 'False'
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
			print("\r["+"*"*p+" "*(50-p)+"]  \033[0;31;42m"+str(i+2)+"\033[0m /"+str(job)+' update_matrix',end="")
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

	def clear_matrix(self,data,gap,match,unmatch,name):
		cleardata = []
		print('\n')
		job = len(data)
		np_p =  np.zeros(shape= (job,job),dtype = int)
		for i in range(job):
			p = int(((i+1)/job)*50)
			print("\r["+"*"*p+" "*(50-p)+"]  \033[0;31;42m"+str(i+1)+"\033[0m /"+str(job)+ '	-> clear',end="")
			for j in range(job):
				if data[-i][-j] >= self.minlength and np_p[-i][-j] == 0: #从后往前遍历，如果当前分数大于最小长度
					cleardata.append(data[-i][-j])
					np_p[-i][-j] = data[-i][-j]
					x,y = i,j
					d = 0
					while 1:
						note = data[-x][-y]
						note1 = data[-x-1][-y-1]
						note2 = data[-x-1][-y]
						note3 = data[-x][-y-1]
						# print('\n',note,note1,note2,note3,x,y)
						if -x-1 > -job and -y-1 > -job and note != 0 and (note == note1 + match or note == note1 + unmatch):
							np_p[-x-1][-y-1] = data[-x-1][-y-1]
							x,y = -(-x-1),-(-y-1)
							d += 1
							continue
						else:
							break
							# exit()
		# 绘制数据分布曲线
		# plt.hist(cleardata, bins=max(cleardata)-min(cleardata)+1, align='left', rwidth=0.8, color='skyblue', edgecolor='black')
		# for i in range(job):
		# 	p = int(((i+1)/job)*50)
		# 	print("\r["+"*"*p+" "*(50-p)+"]  \033[0;31;42m"+str(i+1)+"\033[0m /"+str(job)+ '	-> clear',end="")
		# 	np_p[i][j] = self.minlength

		# print(np_p)


		if len(cleardata) != 0:# 防止数据集为空
			from statistics import mode,median,mean,variance
			# 计算数组的众数
			mode_value = mode(cleardata)
			# 计算数组的均值
			mean_value = mean(cleardata)
			# 计算数组的中位数
			median_value = median(cleardata)
			# 计算数组的方差
			variance_value = variance(cleardata)
		else:
			mode_value,mean_value,median_value,variance_value = 0,0,0,0


		# import math
		# number = int(math.sqrt(len(cleardata))/median_value)+1
		# # number = int(math.sqrt(len(cleardata)))
		# # repeatV = sum(cleardata)/(len(data)-1)
		# repeatV = number/(len(data)-1)

		# return np_p,len(data)-1,repeatV,len(cleardata),mode_value,mean_value,median_value,variance_value,cleardata
		# return np_p,len(data)-1,repeatV,number,mode_value,mean_value,median_value,variance_value,cleardata
		return np_p,len(data)-1,mode_value,mean_value,median_value,variance_value,cleardata

	def np2plot(self,s1,s2,best_matrix,gap,name):

		print('\n')
		np_p =  np.zeros(shape= (len(s2)+1,len(s1)+1),dtype = int)
		np_p[np_p==0] = 255
	
		x,y = [],[]
		job = len(s2)+1
		for i in range(len(s2)+1):
			p = int(((i+1)/job)*50)
			print("\r["+"*"*p+" "*(50-p)+"]  \033[0;31;42m"+str(i+1)+"\033[0m /"+str(job)+ '	-> drawing',end="")
			for j in range(len(s1)+1):
				if best_matrix[i][j] > 0:
					x.append(j)
					y.append(-i)
					np_p[i][j] = 0
		if self.plot == 'True':
			fig = plt.subplots(figsize = (12,12))
			plt.scatter(x, y,s=0.1,c='black')
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

	def get_seed(self,matrix1,name,cleardata,s):
		# print(matrix1)
		indexd = []
		for i in range(len(s)):
			if i <= 2:
				continue
			else:
				if s[i] == s[i-1] and s[i] == s[i-2] and s[i] == s[i-3]:
					indexd.append(i+1)
		# print(indexd,len(indexd))
		# 删除指定列
		matrix1 = np.delete(matrix1, indexd, axis=1)
		matrix1 = np.delete(matrix1, indexd, axis=0)

		# print(matrix1)
		# exit()

		import seaborn as sns
		import matplotlib.pyplot as plt
		sns.violinplot(data=cleardata, color="skyblue") 
		plt.title('Violin Plot of length by Type')
		plt.xlabel('Type')
		plt.ylabel('length')
		plt.savefig(self.workpaths+'./'+name+'-violinplot.png', dpi = 1000, bbox_inches = 'tight')# 存储图片
		plt.close()

		# print(cleardata)
		# upper_quartile = np.percentile(cleardata, 70)
		upper_quartile = np.percentile(cleardata, 50)
		# print(upper_quartile,'###########')

		matrix10 = matrix1.copy()
		matrix = np.where(matrix10 > upper_quartile, 1, 0)

		matrix_p = matrix.copy()
		matrix_p[matrix_p==0] = 255
		from PIL import Image
		data = np.matrix(matrix_p)
		# print('\n',data)
		data = np.reshape(data, (len(matrix_p), len(matrix_p)))
		new_map = Image.fromarray(np.uint8(data))
		new_map.save(self.workpaths+'./'+name+'.png')

		# print(matrix)
		row_sums = list(np.sum(matrix, axis=1)[1:])#行
		# print(row_sums,'每行')
		length = len(s)
		row_sums = [int(length/(i+2)) for i in row_sums]# 添加对角线
		
		row_sums = [num for num in row_sums if num < (length/2)]# 删除长度大于二分之一windows的
		# print(row_sums)


		# from scipy.signal import find_peaks
		# # 绘制数据分布图
		# plt.hist(row_sums, bins=20, density=True, alpha=0.5, color='b')
		# # 执行峰值检测
		# peaks, _ = find_peaks(row_sums, prominence=0.2)  # 调整 prominence 参数以适应你的数据
		# print(peaks)
		# # 绘制峰值点
		# plt.plot(row_sums[peaks], np.full_like(peaks, 0.01), 'ro', markersize=5)

		sns.violinplot(data=row_sums, color="skyblue") 
		# # 获取小提琴图的所有突出部分
		# violins = plt.gca().collections
		# # 打印每个小提琴图的突出部分
		# for violin in violins:
		#	 paths = violin.get_paths()
		#	 print("Number of prominences in this violin:", len(paths))
		plt.title('Violin Plot of length by Type')
		plt.xlabel('Type')
		plt.ylabel('length')
		plt.savefig(self.workpaths+'./'+name+'-violinplot-row_sums.png', dpi = 1000, bbox_inches = 'tight')# 存储图片
		plt.close()

		# 绘制直方图
		hist_data, bin_edges = np.histogram(np.array(row_sums), bins=20)
		print("Histogram data:", hist_data)  # 输出每个柱子的高度
		print("Bin edges:", bin_edges)  # 输出每个桶的边界
		# 找到最高柱子的索引
		max_index = np.argmax(hist_data)
		# 获取最高柱子的边界范围
		start = bin_edges[max_index]
		end = bin_edges[max_index + 1]
		print("Highest bin range:", (start, end))

		# 对柱子高度进行排序，找到第二高的索引
		sorted_indices = np.argsort(hist_data)  # 对柱子高度排序，返回索引
		second_highest_index = sorted_indices[-2]  # 倒数第二个是第二高的索引

		# 获取第二高柱子的区间
		second_high_start = bin_edges[second_highest_index]
		second_high_end = bin_edges[second_highest_index + 1]

		print("Second highest bin range:", (second_high_start, second_high_end))


		plt.hist(np.array(row_sums), bins=20, edgecolor='black')
		plt.title("Histogram of Array Elements")
		plt.xlabel("Element")
		plt.ylabel("Frequency")
		plt.savefig(name+'new-hist.png', dpi = 1000, bbox_inches = 'tight')# 存储图片

		# 创建布尔掩码，保留在 [start, end] 范围内的元素
		mask = (np.array(row_sums) >= start) & (np.array(row_sums) <= end)
		# 使用掩码过滤数组
		filtered_arr = np.array(row_sums)[mask]
		print("Filtered array:", filtered_arr)

		sns.violinplot(data=filtered_arr, color="skyblue") 
		plt.title('Violin Plot of length by Type')
		plt.xlabel('Type')
		plt.ylabel('length')
		plt.savefig(self.workpaths+'./'+name+'-violinplot-row_sumsf.png', dpi = 1000, bbox_inches = 'tight')# 存储图片
		plt.close()

		plt.hist(filtered_arr, bins=10, edgecolor='black')
		plt.title("Histogram of Array Elements")
		plt.xlabel("Element")
		plt.ylabel("Frequency")
		plt.savefig(name+'new-histf.png', dpi = 1000, bbox_inches = 'tight')# 存储图片


		# 创建布尔掩码，保留在 [start, end] 范围内的元素
		mask = (np.array(row_sums) >= second_high_start) & (np.array(row_sums) <= second_high_end)
		# 使用掩码过滤数组
		filtered_arr2 = np.array(row_sums)[mask]
		print("Filtered array:", filtered_arr)

		sns.violinplot(data=filtered_arr2, color="skyblue") 
		plt.title('Violin Plot of length by Type')
		plt.xlabel('Type')
		plt.ylabel('length')
		plt.savefig(self.workpaths+'./'+name+'-violinplot-row_sumsf2.png', dpi = 1000, bbox_inches = 'tight')# 存储图片
		plt.close()

		plt.hist(filtered_arr2, bins=10, edgecolor='black')
		plt.title("Histogram of Array Elements")
		plt.xlabel("Element")
		plt.ylabel("Frequency")
		plt.savefig('new-histf2.png', dpi = 1000, bbox_inches = 'tight')# 存储图片


		if len(row_sums) == 0: # 完全空白
			return 0
		from statistics import mode
		mode_value1 = mode(list(filtered_arr))
		print('\n',mode_value1,'众数f')

		mode_value2 = mode(list(filtered_arr2))
		print('\n',mode_value2,'众数f2')

		mode_value = min(mode_value1,mode_value2)
		print('\n',mode_value,'众数')

		return mode_value

	# 定义正弦函数
	# @staticmethod
	def sinusoidal(self,x, A, B, C, D):
		return A * np.sin(B * x + C) + D

	def AMPD(self,data):
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
		# np.savetxt(self.workpaths+'./plotcsv/'+name+'.csv',best_matrix,fmt='%d',delimiter='\t')
		np.savetxt(self.workpaths+'/'+name+'.one.csv',best_matrix,fmt='%d',delimiter='\t')
		best_matrix1,length,mode_value,mean_value,median_value,variance_value,cleardata = self.clear_matrix(best_matrix,self.gap,1,0,name)
		gc.collect()
		matrix_s = self.read_best_matrix(best_matrix1)
		# seq_mode = self.get_seed(best_matrix1)
		# np.savetxt(self.workpaths+'./clearcsv/'+name+'.csv',best_matrix1,fmt='%d',delimiter='\t')
		np.savetxt(self.workpaths+'/'+name+'.clear.csv',best_matrix1,fmt='%d',delimiter='\t')
		self.np2plot(s1,s2,best_matrix1,self.gap,name)

		for i in range(len(best_matrix1)):
			best_matrix1[i][i] = 1

		# seq_mode = self.get_seed(best_matrix1,name,cleardata,s1)
		print('\t'+name+'\n')
		# exit(0)
		# print(best_matrix1)
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

		np.savetxt(self.workpaths+'/'+name+'.two.csv',np.array(matrix_new),fmt='%d',delimiter='\t')
		# matrix = np.where(np.array(matrix_new) >= 5, 1, 0)# 冗余的一次数据清洗
		matrix = np.where(np.array(matrix_new) >= 1, 1, 0)# 冗余的一次数据清洗

		np.savetxt(self.workpaths+'/'+name+'.clear.two.csv',matrix,fmt='%d',delimiter='\t')
		matrix_p = matrix.copy()
		matrix_p[matrix_p==0] = 255

		col_sums = np.sum(matrix, axis=0)[1:]#列
		x = [i for i in range(len(col_sums))]
		plt.imshow(matrix_p, cmap='gray')
		plt.plot(x, col_sums, alpha=0.6)
		px = self.AMPD(col_sums)

		if len(px) == 0:
			mode_value = 0
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
			print(peakx1, peaky1)

			# 使用嵌套循环计算差值
			differences = []
			for i in range(len(peakx1)):
				if i+2 >= len(peakx1):
					continue
				for j in range(i + 1, i + 2):
					seedlength = abs(peakx1[i] - peakx1[j])
					if seedlength >= self.minlength:
						differences.append(seedlength)  # 计算绝对差值

			# print("All differences:", differences)
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

		plt.legend()  # 显示图例
		plt.yticks([])
		plt.savefig(self.workpaths+'./hist/'+name+'.png', dpi = 600, bbox_inches = 'tight')# 存储图片
		plt.close()

		gc.collect()
		GC = (s1.count('G')+s1.count('C'))/len(s1)
		seq_mode = mode_value
		seq0 = s1[:seq_mode]
		return [length,GC,number,mode_value,mean_value,median_value,variance_value,seq_mode]+matrix_s+[seq0]


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
		if not os.path.exists(self.workpaths+self.pilpath):
			os.makedirs(self.workpaths+self.pilpath)
		if not os.path.exists(self.workpaths+self.histpath):
			os.makedirs(self.workpaths+self.histpath)

		# if not os.path.exists(self.workpaths+'./plotcsv/'):
		# 	os.makedirs(self.workpaths+'./plotcsv/')
		# if not os.path.exists(self.workpaths+'./clearcsv/'):
		# 	os.makedirs(self.workpaths+'./clearcsv/')

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
		print("\n********************输出********************")

		names = list(results.keys())
		maker = ['length','GC','number','mode_value','mean_value','median_value','variance_value','seed_l']+['M'+str(i) for i in range(1,201)]+['seed']
		f = open(self.workpath+self.outfile,'w')
		f.write('\t'.join(['chr','dotplot','name','start','end']+maker)+'\n')
		# value = [[],[],[],[],[],[],[],[]]
		value = [[] for _ in range(210)]
		for j in range(len(names)):
			name = names[j]
			lt = results[name]['value'].get()
			for i in range(len(lt)):
				value[i].append(lt[i])
				# ax[i].set_title(maker[i])
				# ax[i].plot([j],[lt[i]],"o",label = name)
			lt = results[name]['gff'] + lt
			f.write('\t'.join([str(s) for s in lt])+'\n')


		# import matplotlib.pyplot as plt
		# fig,ax=plt.subplots(3,figsize=(2,10),dpi=800)
		# ax[0].set_title('mean-rV')
		# ax[0].plot(value[5],value[2],"o", markersize=1)

		# ax[1].set_title('mean-median')
		# ax[1].plot(value[5],value[6],"o", markersize=1)

		# ax[2].set_title('mean-variance')
		# ax[2].plot(value[5],value[7],"o", markersize=1)

		# plt.xlabel('mean')# 设置 x 轴标签
		# plt.ylabel('countV')# 设置 y 轴标签
		# plt.savefig(self.workpaths+'xx.png', dpi = 1000, bbox_inches = 'tight')# 存储图片
		# # 清除画布
		# plt.close()

		f.close()


