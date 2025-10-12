# python
# -*- encoding: utf-8 -*-
'''
@File        :bio.py
@Time        :2021/04/27 19:54:08
@Author        :charles kiko
@Version        :1.0
@Contact        :charles_kiko@163.com
@Desc        :python bio.py gff pep cds ncbi/embl xxx
@annotation        :
'''

import sys
import ast
import os
import gc# 内存管理模块
from tqdm import trange
from Bio.Seq import Seq
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

import numpy as np
import pandas as pd
import CentriVision.bez as bez

class getNCBI():
    def __init__(self, options):
        self.gene_r8_Separator1 = ';' # 基因注释外部分隔符
        self.gene_r8_Separator2 = '=' # 基因注释名与注释值分隔符
        self.gene_row_key = 'ID'
        self.mrna_gene_key = 'Parent'
        self.mrna_row_key = 'ID'
        # self.gff3_file = 'x.gff3'
        # self.pep_file = 'x.gff3'
        # self.cds_file = 'x.gff3'
        # self.species = 'x.gff3'
        self.gene_file = 'None'
        self.genome_file = 'None'
        for k, v in options:
            setattr(self, str(k), v)
            print(k, ' = ', v)

    def read_r8(self,s):
        dic = {}
        lt = s.split(self.gene_r8_Separator1)
        for i in lt:
            if self.gene_r8_Separator2 in i:
                lt0 = i.split(self.gene_r8_Separator2)
                dic[lt0[0]] = lt0[1]
        return dic

    def get_chr(self,chr0,maker,index):
        return self.species + chr0.split(maker)[index]
        # return self.species + chr0[3:]

    def ncbi_gff(self):
        if os.path.exists(self.species+'_gene.gff'):
            os.remove(self.species+'_gene.gff')
        if os.path.exists(self.species+'_mrna.gff'):
            os.remove(self.species+'_mrna.gff')
        if os.path.exists(self.species+'.cds'):
            os.remove(self.species+'.cds')
        if os.path.exists(self.species+'.pep'):
            os.remove(self.species+'.pep')


        gff = pd.read_csv(self.gff3_file,header = None, sep='\t', comment='#')
        print(gff)
        print("************************************************** 注意 **************************************************")
        a = input("如果染色体名称需要稍作修改(EVM_01 -> at01,默认修改为EVM_01 -> atEVM_01)请选择Y,不需要则输入N or enter:\n")
        if a == "Y":
            maker = input("请输入染色体ID的分割符号：")
            index = input("请输入染色体ID分割后保留序号：")
            print("将输出如下ID:",self.species+str(gff.iloc[0, 0]).split(maker)[int(index)])
            gff[0] = gff.apply(lambda row: self.get_chr(row[0],maker,int(index)), axis = 1)
            print(gff)
            if self.genome_file != "None":
                a = input("若基因组染色体名称需要稍作修改(EVM_01 -> at01,默认修改为EVM_01 -> atEVM_01)请选择Y,不需要则输入N or enter:\n")
                if a != "Y":
                    genome = self.readncbigenome0()
                else:
                    genome = self.readncbigenome(self.genome_file,maker,int(index))
            else:
                print("缺失genome文件之后lens文件染色体长度默认为染色体末位基因结尾\n请注意！！！")
        else:
            #gff[0] = gff.apply(lambda row: self.get_chr(row[0],' ',0), axis = 1)
            if self.genome_file != "None":
                a = input("若基因组染色体名称需要稍作修改(EVM_01 -> at01,默认修改为EVM_01 -> atEVM_01)请选择Y,不需要则输入N or enter:\n")
                if a != "Y":
                    genome = self.readncbigenome0()
                else:
                    genome = self.readncbigenome(self.genome_file,maker,int(index))
                # genome = self.readncbigenome0()
                #genome = self.readncbigenome(self.genome_file,' ',0)
            else:
                print("缺失genome文件之后lens文件染色体长度默认为染色体末位基因结尾\n请注意！！！")

        dic = gff.groupby(2).groups# 按照第几列分组
        gene = gff.loc[dic['gene']].sort_values(by=[0,3],ascending= [True,True])
        gene.reset_index(drop=True,inplace=True)
        # print(gene)

        # 基因分染色体
        lens = open(self.species+".lens",'w')
        dic0 = gene.groupby(0).groups
        gene_dic = {}
        for key in dic0.keys():
            print(" ******** ",key," ******** ")
            local = gene.loc[dic0[key]].sort_values(by=[0,3],ascending= [True,True])
            local.reset_index(drop=True,inplace=True)
            print(local)
            for index,row in local.iterrows():
                name = row[0] + 'g' + str(index+1).zfill(4)
                local.loc[index,1] = name
                old_name = self.read_r8(row[8])[self.gene_row_key]
                local.loc[index,8] = old_name
                local.loc[index,7] = index+1
                gene_dic[old_name] = name
            row_1 = local.iloc[-1].tolist()
            if self.genome_file != "None":
                #print(genome.keys())
                lens_s = [key,str(len(genome[key].seq)),str(int(row_1[7]))]
            else:
                lens_s = [key,str(row_1[4]),str(int(row_1[7]))]
            lens.write('\t'.join(lens_s)+'\n')
            local = local[[0,1,3,4,6,7,8]]
            local.to_csv(self.species+'_gene.gff', index=False, header=False,sep='\t',mode='a+')
            print(local)
        del dic0,local

        pepdoc = self.readncbipep(self.pep_file,' ',0)
        cdsdoc = self.readncbicds(self.cds_file,' ',0)
        print("\n************************************************** 注意 **************************************************")
        mrna = gff.loc[dic['mRNA']].sort_values(by=[0,3],ascending= [True,True])
        mrna.reset_index(drop=True,inplace=True)
        first_row = mrna.iloc[0]
        print(first_row)
        print('self.mrna_row_key ',self.mrna_row_key)
        print('pep file ID ',list(pepdoc.keys())[0])
        print('cds file ID ',list(cdsdoc.keys())[0])
        print('If the protein ID and CDS ID formats are inconsistent, the code needs to be modified.')

        a = input('请输入需要修改的文件 C/P/CP or None\n')
        if a == 'C' or a.upper() == 'C':
            print('cds file ID ',list(cdsdoc.keys())[0])
            maker = input("请输入CDS序列ID的分割符号：")
            index = input("请输入CDS序列ID分割后保留序号：")
            print("将输出如下ID:",list(cdsdoc.keys())[0].split(maker)[int(index)])
            cdsdoc = self.readncbicds(self.cds_file,maker,int(index))
        elif a == 'P' or a.upper() == 'P':
            print('pep file ID ',list(pepdoc.keys())[0])
            maker = input("请输入PEP序列ID的分割符号：")
            index = input("请输入PEP序列ID分割后保留序号：")
            print("将输出如下ID:",list(pepdoc.keys())[0].split(maker)[int(index)])
            pepdoc = self.readncbipep(self.pep_file,maker,int(index))
        elif a == 'CP' or a.upper() == 'CP':
            print('cds file ID ',list(cdsdoc.keys())[0])
            print('pep file ID ',list(pepdoc.keys())[0])
            maker = input("请输入CDS序列ID的分割符号：")
            index = input("请输入CDS序列ID分割后保留序号：")
            print("将输出如下ID:",list(cdsdoc.keys())[0].split(maker)[int(index)])
            cdsdoc = self.readncbicds(self.cds_file,maker,int(index))
            maker = input("请输入PEP序列ID的分割符号：")
            index = input("请输入PEP序列ID分割后保留序号：")
            print("将输出如下ID:",list(pepdoc.keys())[0].split(maker)[int(index)])
            pepdoc = self.readncbipep(self.pep_file,maker,int(index))
        elif a == 'None' or a == '':
            pass
        else:
            pass

        pep = open(self.species+'.pep','w')
        cds = open(self.species+'.cds','w')
        pepdoc1,cdsdoc1 = {},{}
        
        
        dic0 = mrna.groupby(0).groups
        # mrna_dic = {}
        for key in dic0.keys():
            print(" ******** ",key," ******** ")
            local = mrna.loc[dic0[key]].sort_values(by=[0,3],ascending= [True,True])
            local.reset_index(drop=True,inplace=True)
            print(local)
            for index,row in local.iterrows():
                gene_name = self.read_r8(row[8])[self.mrna_gene_key]
                tran_name = self.read_r8(row[8])[self.mrna_row_key]
                name = gene_dic[gene_name]
                local.loc[index,1] = name
                local.loc[index,8] = gene_name
                # gene_dic[old_name] = name
                if name not in cdsdoc1.keys() and tran_name in cdsdoc.keys() and tran_name in pepdoc.keys():
                    cdsdoc1[name] = SeqRecord(Seq(str(cdsdoc[tran_name].seq)),id=name,name=name,description=gene_name)
                    pepdoc1[name] = SeqRecord(Seq(str(pepdoc[tran_name].seq)),id=name,name=name,description=gene_name)
                elif name in cdsdoc1.keys() and tran_name in cdsdoc.keys() and tran_name in pepdoc.keys():
                    if len(str(cdsdoc[tran_name].seq)) > len(str(cdsdoc1[name].seq)):
                        cdsdoc1[name] = SeqRecord(Seq(str(cdsdoc[tran_name].seq)),id=name,name=name,description=gene_name)
                        pepdoc1[name] = SeqRecord(Seq(str(pepdoc[tran_name].seq)),id=name,name=name,description=gene_name)
                    else:
                        continue
            local = local[[0,1,2,3,4,6,7,8]]
            local.reset_index(drop=True,inplace=True)
            local[2] = 'mRNA'
            local.to_csv(self.species+'_mrna.gff', index=False, header=False,sep='\t',mode='a+')
            print(local)
        for key in cdsdoc1.keys():
            SeqIO.write(cdsdoc1[key], cds, "fasta")
            SeqIO.write(pepdoc1[key], pep, "fasta")

        pep.close()
        cds.close()


    def genenum(self,gfflist):
        num = 0# 计数
        for gff in gfflist:
            if gff[2] == 'gene':
                num += 1
            else:
                pass
        k = len(str(num))
        return k

    def readncbipep(self,file,maker,index):
        print('reading ncbi-pep')
        pep = {}
        for seq_record in SeqIO.parse(file, "fasta"):# biopython循环读取
            gene = str(seq_record.id).split(maker)[index]
            pep[gene] = seq_record
        print('pep of number is ',len(pep))
        return pep

    def readncbicds(self,file,maker,index):
        print('reading ncbi-cds')
        cds = {}
        for seq_record in SeqIO.parse(file, "fasta"):# biopython循环读取
            gene = str(seq_record.id).split(maker)[index]
            cds[gene] = seq_record
        print('cds of number is ',len(cds))
        return cds

    def readncbigenome(self,file,maker,index):
        print('reading ncbi-genome')
        genome = {}
        for seq_record in SeqIO.parse(file, "fasta"):# biopython循环读取
            gene = self.species + str(seq_record.id).split(maker)[index]
            genome[gene] = seq_record
        print('genome of number is ',len(genome))
        return genome

    def readncbigenome0(self):
        print('reading genome')
        genome = SeqIO.to_dict(SeqIO.parse(self.genome_file, "fasta"))# 提取之后直接返回字典
        print('Chr of number is ',len(genome))
        return genome

    def readncbipep0(self):
        print('reading ncbi-pep')
        pep = SeqIO.to_dict(SeqIO.parse(self.pep_file, "fasta"))# 提取之后直接返回字典
        print('PEP of number is ',len(pep))
        return pep

    def readncbigene0(self):
        print('reading ncbi-gene')
        cds = {}
        for seq_record in SeqIO.parse(sys.argv[2], "fasta"):# biopython循环读取
            gene = str(seq_record.id).split('CDS')[0][:-1]
            cds[gene] = seq_record
        print('gene of number is ',len(cds))
        return cds

    def readncbicds0(self):
        print('reading ncbi-cds')
        cds = SeqIO.to_dict(SeqIO.parse(self.cds_file, "fasta"))# 提取之后直接返回字典
        print('CDS of number is ',len(cds))
        return cds

    def sequence(self,chrlist):
        newchr = {}
        doc = {}
        for i in chrlist:
            doc[str(i)] = int(i[1])
        dic1SortList = sorted(doc.items(),key = lambda x:x[1],reverse = True)
        for j in range(len(dic1SortList)):
            lt0 = ast.literal_eval(dic1SortList[j][0])
            lt0.append(j + 1)
            newchr[lt0[0]] = lt0
        return newchr

    def filewrite(self,file,name,seq):
        f = open(file,'a+',encoding = 'utf-8')
        f.write('>' + name + '\n')
        f.write(seq)
        f.close()

    def writegff(self,file,lt):
        f = open(file,'a+',encoding = 'utf-8')
        f.write(str(self.species) + str(lt[0]) + '\t' + str(lt[1]) + '\t' \
            + str(lt[2]) + '\t' + str(lt[3]) + '\t' \
            + str(lt[4]) + '\t' +str(lt[5]) + '\t' \
            +str(lt[6]) + '\n')
        f.close()

    def writelens(self,file,lt):
        f = open(file,'a+',encoding = 'utf-8')
        f.write(str(self.species) + str(lt[0]) + '\t' + str(lt[1]) + '\t' \
            + str(lt[2]) + '\n')
        f.close()

    def runncbi(self):
        self.ncbi_gff()
        exit()

        pepdoc = self.readncbipep()
        cdsdoc = self.readncbicds()
        genenum = self.genenum(gfflist)
        chrdoc1 = self.sequence(chrlist)
        genenums = 0
        print('gff文件筛选及cds、pep生成')
        for i in trange(len(gfflist)):
            gffrow = gfflist[i]
            if gffrow[2] == 'mRNA':
                gene = str(gffrow[8]['gene'])## 注意
                if gene in cdsdoc.keys() and str(cdsdoc[gene][0]) in pepdoc.keys():
                    genenums += 1
                    ol_chr = str(gffrow[0])
                    if len(str(chrdoc1[ol_chr][0])) <= 10 and str(chrdoc1[ol_chr][0]) != 'Unknown':
                        newchrname = chrdoc1[ol_chr][-2]
                    else:
                        newchrname = chrdoc1[ol_chr][-1]
                    # 在这儿修改名字，需求按照染色体长度排序
                    newname = self.species + str(newchrname) + 'g' + str(genenums).zfill(genenum)
                    self.filewrite(self.species + '.pep',newname,pepdoc[str(cdsdoc[gene][0])])
                    self.filewrite(self.species + '.cds',newname,cdsdoc[gene][1])
                    lt0 = [gffrow[0],gffrow[3],gffrow[4],gffrow[6],str(gene),newchrname,newname]
                    self.gff.append(lt0)
                elif gene in cdsdoc.keys():
                    genenums += 1
                    ol_chr = str(gffrow[0])
                    if len(str(chrdoc1[ol_chr][0])) <= 10 and str(chrdoc1[ol_chr][0]) != 'Unknown':
                        newchrname = chrdoc1[ol_chr][-2]
                    else:
                        newchrname = chrdoc1[ol_chr][-1]
                    # 在这儿修改名字，需求按照染色体长度排序
                    newname = self.species + str(newchrname) + 'g' + str(genenums).zfill(genenum)
                    # self.filewrite(self.species + '.pep',newname,pepdoc[str(cdsdoc[gene][0])])
                    self.filewrite(self.species + '.cds',newname,cdsdoc[gene][1])
                    lt0 = [gffrow[0],gffrow[3],gffrow[4],gffrow[6],str(gene),newchrname,newname]
                    self.gff.append(lt0)
                else:
                    pass
        gc.collect()# 内存释放
        genenum1 = 1
        chrlist0 = []
        chr0 = []
        print('gff、lens生成')
        for i in trange(len(self.gff)):
            gene = self.gff[i]
            if gene[-2] not in chrlist0:
                if chr0 != []:
                    self.writelens(str(self.species) + '.lens', chr0)
                    chr0 = []
                chrlist0.append(gene[-2])
                genenum1 = 1
                lt = [gene[-2],gene[-1],gene[1],gene[2],gene[3],genenum1,gene[4]]
                self.writegff(str(self.species) + '.gff', lt)
            else:
                genenum1 += 1
                chr0 = []
                chr0 = chr0 + [gene[-2],chrdoc1[gene[0]][1],genenum1]
                lt = [gene[-2],gene[-1],gene[1],gene[2],gene[3],genenum1,gene[4]]
                self.writegff(str(self.species) + '.gff', lt)
        if chr0 != []:
            self.writelens(str(self.species) + '.lens', chr0)

    def run(self):
        self.runncbi()


# data = getNCBI()
# data.run()
