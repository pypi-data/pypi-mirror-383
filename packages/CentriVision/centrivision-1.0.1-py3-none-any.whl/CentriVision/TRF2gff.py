# TRF2gff
import sys
dat = open(sys.argv[1],'r').read()
dat = dat.split('Sequence: ')
print(len(dat))
gff = open(sys.argv[2],'w')
TRF = open(sys.argv[3],'w')
gff.write('')
chro = ''
num = 0
for i in range(1,len(dat)):
	lt = dat[i].split('\n')
	#print(len(lt))
	for line in lt:
		lt0 = line.split()
		if len(lt0) == 1:
			chro = lt0[0]
		elif len(lt0) == 0 or lt0[0] == 'Parameters:':
			continue
		else:
			# print(len(lt0))
			num += 1
			ID = 'TRF'+str(num).zfill(5)
			out_l = [chro,'TRF','TandemRepeat',lt0[0],lt0[1],'','','',"ID="+ID+";PeriodSize="+str(lt0[2])+';CopyNumber='+str(lt0[3])+';Consensus='+lt0[-2]]
			print(out_l)
			ID = '>'+ID+'#TRF'
			seq = lt0[-1]
			gff.write('\t'.join(out_l)+"\n")
			TRF.write(ID+'\n'+seq+'\n')
gff.close()
TRF.close()
