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
import numpy as np
import pandas as pd
class Dotplot():
	def __init__(self, options):
		self.workpath = os.getcwd()+'/'
		self.workpaths = './Dotplot/'
		self.fastapath = './fasta/'
		self.plotpath = './plot/'
		self.pilpath = './PIL/'
		self.histpath = './hist/'
		self.cpu = 16
		self.gap = -10
		self.windows = 4000
		self.minlength = 8
		self.konbai = 20
		self.poly = 'False'
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
		if self.cpu > cpu_count():
			self.cpu = cpu_count()

	# def get_match_score(self,s1,s2,score_matrix):	#获取替换打分
	# 	# global  score_matrix
	# 	s = ['A','G','C','T'].index(s2)
	# 	score = score_matrix[s1][s]
	# 	return score


	def update_best_matrix(self,s1,s2,best_matrix,gap):
		job = len(s2)+1
		for i in range(len(s2)):
			p = int(((i+1)/job)*100)
			print("\r["+"*"*p+" "*(100-p)+"]  \033[0;31;42m"+str(i)+"\033[0m /"+str(job)+' update_matrix',end="")
			for j in range(len(s1)):
				if i == 0 or j == 0 or i == j:
					best_matrix[i][j] = 0
				else:
					# match = self.get_match_score(s2[i-1],s1[j-1],score_matrix)
					# if j >= 2 and i >= 2 and self.poly == 'True':# 舍弃单碱基重复
					# 	if s2[i-2] == s1[j-2] and s2[i-1] == s2[i-2]:
					# 		match = 0
					# match_score = best_matrix[i-1][j-1]+match
					# score = max(match_score,0)
					# best_matrix[i][j] = score
					if s2[i-1] != s1[j-1] or s2[i-1] == 'N' or s1[j-1] == 'N':
						best_matrix[i][j] = 0
					else:
						match = 1
						if j >= 2 and i >= 2 and self.poly == 'True':# 舍弃单碱基重复
							if s2[i-2] == s1[j-2] and s2[i-1] == s2[i-2]:
								match = 0
						match_score = best_matrix[i-1][j-1]+match
						best_matrix[i][j] = match_score
		return best_matrix

	def clear_matrix(self,data,gap,match,unmatch,name):
		cleardata = []
		print('\n')
		job = len(data)
		np_p =  np.zeros(shape= (job,job),dtype = int)
		for i in range(job):
			p = int(((i+1)/job)*100)
			print("\r["+"*"*p+" "*(100-p)+"]  \033[0;31;42m"+str(i+1)+"\033[0m /"+str(job)+ '	-> clear',end="")
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
						# elif -x-1 > -job and -y > -job and note != 0 and note == note2 + gap:
						# 	np_p[-x-1][-y] = data[-x-1][-y]
						# 	x,y = -(-x-1),-(-y)
						# 	d += 1
						# 	continue
						# elif -x > -job and -y-1 > -job and note != 0 and note == note3 + gap:
						# 	np_p[-x][-y-1] = data[-x][-y-1]
						# 	x,y = -(-x),-(-y-1)
						# 	d += 1
						# 	continue
						else:
							break
							# exit()

		# 绘制数据分布曲线
		# plt.hist(cleardata, bins=max(cleardata)-min(cleardata)+1, align='left', rwidth=0.8, color='skyblue', edgecolor='black')

		repeatV = sum(cleardata)/(len(data)-1)

		# import matplotlib.pyplot as plt
		# fig = plt.subplots(figsize = (12,12))
		# plt.hist(cleardata,100,alpha=0.4,label=name, color='skyblue', edgecolor='black')
		# # 添加标题和标签
		# plt.title('repeatnumber:'+str(len(cleardata))+';repeatV:'+str(repeatV))
		# plt.xlabel('Data')
		# plt.ylabel('Frequency')
		# # 显示图形
		# plt.savefig(self.workpaths+self.histpath+name+'.png',dpi = 600, bbox_inches = 'tight')
		# # 清除画布
		# plt.close()

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
		return np_p,len(data)-1,repeatV,len(cleardata),mode_value,mean_value,median_value,variance_value

	def np2plot2(self,s1,s2,best_matrix,best_matrix2,gap,name):
		print('\n')
		np_p =  np.zeros(shape= (len(s2)+1,len(s1)+1),dtype = int)
		np_p[np_p==0] = 255
		x,y = [],[]
		job = len(s1)+1
		for i in range(len(s1)+1):
			p = int(((i+1)/job)*100)
			print("\r["+"*"*p+" "*(100-p)+"]  \033[0;31;42m"+str(i)+"\033[0m /"+str(job)+ '	-> drawing',end="")
			for j in range(len(s1)+1):
				if best_matrix[i][j] > 0:
					x.append(j)
					y.append(-i)
					np_p[i][j] = 0

		job = len(s2)+1
		for i in range(len(s2)+1):
			p = int(((i+1)/job)*100)
			print("\r["+"*"*p+" "*(100-p)+"]  \033[0;31;42m"+str(i)+"\033[0m /"+str(job)+ '	-> drawing1',end="")
			for j in range(len(s2)+1):
				if best_matrix2[i][j] > 0:
					x.append(j)
					y.append(-i)
					np_p[i][j] = 0



		import matplotlib.pyplot as plt
		fig = plt.subplots(figsize = (12,12))
		plt.scatter(x, y,s=0.1,c='black')
		plt.xlim(0,job)
		plt.ylim(-job,0)
		# plt.axis('off')
		plt.savefig(self.workpaths+'./plot/'+name+'.png',dpi = 1000, bbox_inches='tight')	
		# plt.show()
		# 清除画布
		plt.close()
		# np.savetxt('./PILCSV/'+name+'.csv',np_p,fmt='%d',delimiter='\t')
		from PIL import Image
		data = np.matrix(np_p)
		# print('\n',data)
		data = np.reshape(data, (job, job))
		new_map = Image.fromarray(np.uint8(data))
		# new_map.show()
		new_map.save(self.workpaths+'./PIL/'+name+'.png')
		# print('\n')

	def np2plot(self,s1,s2,best_matrix,gap,name):
		print('\n')
		np_p =  np.zeros(shape= (len(s2)+1,len(s1)+1),dtype = int)
		np_p[np_p==0] = 255
		x,y = [],[]
		job = len(s2)+1
		for i in range(len(s2)+1):
			p = int(((i+1)/job)*100)
			print("\r["+"*"*p+" "*(100-p)+"]  \033[0;31;42m"+str(i)+"\033[0m /"+str(job)+ '	-> drawing',end="")
			for j in range(len(s1)+1):
				if best_matrix[i][j] > 0:
					x.append(j)
					y.append(-i)
					np_p[i][j] = 0
		import matplotlib.pyplot as plt
		fig = plt.subplots(figsize = (12,12))
		plt.scatter(x, y,s=0.1,c='black')
		plt.xlim(0,job)
		plt.ylim(-job,0)
		# plt.axis('off')
		plt.savefig(self.workpaths+'./plot/'+name+'.png',dpi = 1000, bbox_inches='tight')	
		# plt.show()
		# 清除画布
		plt.close()
		# np.savetxt('./PILCSV/'+name+'.csv',np_p,fmt='%d',delimiter='\t')
		from PIL import Image
		data = np.matrix(np_p)
		# print('\n',data)
		data = np.reshape(data, (job, job))
		new_map = Image.fromarray(np.uint8(data))
		# new_map.show()
		new_map.save(self.workpaths+'./PIL/'+name+'.png')
		# print('\n')

	# def condense_array(self,original_array, new_length=101):
	# 	old_length = len(original_array)
	# 	indices = np.linspace(0, old_length - 1, new_length).astype(int)
	# 	condensed_array = np.interp(np.arange(new_length), indices, original_array)
	# 	return condensed_array

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
		# 对每行求和
		row_sums = np.sum(matrix, axis=1)[1:]#行
		col_sums = np.sum(matrix, axis=0)[1:]#列
		# 将数组浓缩为长度为100的数组
		row_sums = list(self.condense_array(row_sums))
		col_sums = list(self.condense_array(col_sums))
		matrix_s = row_sums+col_sums
		# del matrix,row_sums,col_sums
		return [float(i)/(len(matrix)-1) for i in matrix_s]

	def get_seed(self,matrix):
		# print('\n',matrix)
		matrix = np.int64(matrix>0)
		# print(matrix)
		row_sums = list(np.sum(matrix, axis=1)[1:])#行
		length = len(row_sums)
		row_sums = [int(length/(i+1)) for i in row_sums]# 添加对角线
		row_sums = [num for num in row_sums if num <= 600]# 删除长度大于600的
		# print(row_sums)
		if len(row_sums) < self.konbai:# 如果长度小于600的数量太少也就是空白图
			return 0
		else:
			from statistics import mode
			mode_value = mode(row_sums)
			return mode_value

	def start(self,s1,s2,name):
		best_matrix = np.zeros(shape= (len(s2)+1,len(s1)+1),dtype = int)	#初始化得分矩阵
		best_matrix = self.update_best_matrix(s1,s1,best_matrix,self.gap)
		best_matrix2 = self.update_best_matrix(s2,s2,best_matrix,self.gap)
		gc.collect()
		# np.savetxt(self.workpaths+'./plotcsv/'+name+'.csv',best_matrix,fmt='%d',delimiter='\t')
		best_matrix2,length,repeatV,number,mode_value,mean_value,median_value,variance_value = self.clear_matrix(best_matrix2,self.gap,1,0,name)
		best_matrix1,length,repeatV,number,mode_value,mean_value,median_value,variance_value = self.clear_matrix(best_matrix,self.gap,1,0,name)
		gc.collect()
		matrix_s = self.read_best_matrix(best_matrix1)
		seq_mode = self.get_seed(best_matrix1)
		# np.savetxt(self.workpaths+'./clearcsv/'+name+'.csv',best_matrix1,fmt='%d',delimiter='\t')
		# self.np2plot(s1,s1,best_matrix1,self.gap,name)
		self.np2plot2(s1,s2,best_matrix1,best_matrix2,self.gap,name)
		gc.collect()
		GC = (s1.count('G')+s1.count('C'))/len(s1)
		# seq_mode = 0
		seq0 = s1[:seq_mode]
		return [length,GC,repeatV,number,mode_value,mean_value,median_value,variance_value,seq_mode]+matrix_s+[seq0]


	def run(self):
		pool = multiprocessing.Pool(processes = self.cpu)
		genome = SeqIO.to_dict(SeqIO.parse(self.genome_file, "fasta"))
		if not os.path.exists(self.workpaths):
			# 如果文件夹不存在，则创建文件夹
			os.makedirs(self.workpaths)
		if not os.path.exists(self.workpaths+self.fastapath):
			os.makedirs(self.workpaths+self.fastapath)
		if not os.path.exists(self.workpaths+self.plotpath):
			os.makedirs(self.workpaths+self.plotpath)
		if not os.path.exists(self.workpaths+self.pilpath):
			os.makedirs(self.workpaths+self.pilpath)
		if not os.path.exists(self.workpaths+self.histpath):
			os.makedirs(self.workpaths+self.histpath)

		# if not os.path.exists(self.workpaths+'./plotcsv/'):
		# 	os.makedirs(self.workpaths+'./plotcsv/')
		# if not os.path.exists(self.workpaths+'./clearcsv/'):
		# 	os.makedirs(self.workpaths+'./clearcsv/')

		f = open(self.workpaths+self.fastapath+'split.fasta','w')
		f1 = open(self.workpaths+self.fastapath+'split.gff','w')
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
				s1,s2 = s0,s0[::-1]
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
		maker = ['length','GC','repeatV','number','mode_value','mean_value','median_value','variance_value','seed_l']+['M'+str(i) for i in range(1,201)]+['seed']
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

