# python
# -*- encoding: utf-8 -*-
'''
@File        :getPASA.py
@Time        :2021/04/27 19:54:08
@Author        :charles kiko
@Version        :1.0
@Contact        :charles_kiko@163.com
@Desc        :python getPASA.py oldgff oldpep oldcds oldgene genome xxx
@annotation        :
'''

import sys
import os
import gc# 内存管理模块
from tqdm import trange
from Bio.Seq import Seq
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
import numpy as np
import pandas as pd
import CentriVision.bez as bez

class getPASA():
    def __init__(self, options):
        self.gene_r8_Separator1 = ';' # 基因注释外部分隔符
        self.gene_r8_Separator2 = '=' # 基因注释名与注释值分隔符
        self.gene_row_key = 'ID'
        self.mrna_gene_key = 'Parent'
        self.mrna_row_key = 'ID'
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

    def getgene_r8(self,s,types):
        dic = {}
        lt = s.split(self.gene_r8_Separator1)
        for i in lt:
            if self.gene_r8_Separator2 in i:
                lt0 = i.split(self.gene_r8_Separator2)
                dic[lt0[0]] = lt0[1]
        if types == 'gene':
            return dic['ID']
        elif types == 'mRNA':
            return dic['Parent']
        else:
            return dic['Parent'].replace("model", "TU")

    def getgene_r81(self,s,types):
        dic = {}
        lt = s.split(self.gene_r8_Separator1)
        for i in lt:
            if self.gene_r8_Separator2 in i:
                lt0 = i.split(self.gene_r8_Separator2)
                dic[lt0[0]] = lt0[1]
        if types == 'gene':
            return dic['ID']
        elif types == 'mRNA':
            return dic['Parent']
        else:
            return dic['Parent']

    def ncbi_gff(self):
        # if os.path.exists(self.species+'_gene.gff'):
        #     os.remove(self.species+'_gene.gff')
        # if os.path.exists(self.species+'_mrna.gff'):
        #     os.remove(self.species+'_mrna.gff')
        # if os.path.exists(self.species+'.cds'):
        #     os.remove(self.species+'.cds')
        # if os.path.exists(self.species+'.pep'):
        #     os.remove(self.species+'.pep')
        # if os.path.exists(self.species+'.gene.fa'):
        #     os.remove(self.species+'.gene.fa')
        # if os.path.exists(self.species+'_cds.gff3'):
        #     os.remove(self.species+'_cds.gff3')
        # if os.path.exists(self.species+'_exon.gff3'):
        #     os.remove(self.species+'_exon.gff3')
        # if os.path.exists(self.species+'.lens'):
        #     os.remove(self.species+'.lens')

        genome = self.readncbigenome()
        pepdoc,pepc = self.readncbipep()
        cdsdoc,cdsc = self.readncbicds()
        genedoc = self.readncbigene(list(pepdoc.keys()),cdsc)

        lensf = open(self.species+'.lens','w')
        pepf = open(self.species+'.pep','w')
        cdsf = open(self.species+'.cds','w')
        genef = open(self.species+'.gene.fa','w')
        gffout = open(self.species+'_gene.gff','w')
        cdsgffout = open(self.species+'_cds.gff3','w')
        exongffout = open(self.species+'_exon.gff3','w')

        gff = pd.read_csv(self.gff3_file,header = None, sep='\t', comment='#')
        gff[9]=gff.apply(lambda x:self.getgene_r8(x[8],x[2]),axis=1)
        chrsgff = gff.groupby(0).groups
        for key in chrsgff.keys():# 遍历染色体
            print(" ******** ",key," ******** ")
            local = gff.loc[chrsgff[key]]
            local.reset_index(drop=True,inplace=True)
            print(local)
            chr_gene_dic0 = local.groupby(9).groups# 按照第几列分组
            genegff = local.groupby(2).groups# 按照第几列分组
            genepd = local.loc[genegff['gene']].sort_values(by=[0,3],ascending= [True,True])
            genepd.reset_index(drop=True,inplace=True)
            print(genepd,'\n',len(genepd))
            lens = [key,str(len(genome[key].seq)),str(len(genepd))]
            lensf.write('\t'.join(lens)+'\n')
            for index,row in genepd.iterrows():# 遍历基因
                name = row[0] + 'g' + str(index+1).zfill(4)
                gene = local.loc[chr_gene_dic0[row[9]]]
                gene[10] = gene.apply(lambda x:self.getgene_r81(x[8],x[2]),axis=1)
                kripke = gene.groupby(2).groups# 按照第几列分组
                mRNA = gene.loc[kripke['mRNA']].sort_values(by=[0,3],ascending= [True,True])
                mRNA.reset_index(drop=True,inplace=True)
                oldid = mRNA.iloc[0, 9]
                pep_seq,cds_seq,gene_seq = '','',''
                pepname = ''
                for index1,row in mRNA.iterrows():# 遍历基因的mrna结构
                    dic = self.read_r8(row[8])
                    if dic['ID'] in pepdoc.keys():
                        pep_seq = pepdoc[dic['ID']]
                        cds_seq = cdsdoc[dic['ID']]
                        pepname = dic['ID']
                        break
                if pepname == '':
                    for index1,row in mRNA.iterrows():# 遍历基因的mrna结构
                        pep_seq = pepdoc[pepc[row[9]]]
                        cds_seq = cdsdoc[pepc[row[9]]]
                        pepname = pepc[row[9]]
                        break
                if pepname == '':
                    print(oldid,pepname,' 基因不存在？')
                    exit()

                try:
                    gene_seq = genedoc[pepname]
                except:
                    print(pepname,' 这个基因没有找到gene序列')
                    exit()

                cds_s = SeqRecord(Seq(str(cds_seq.seq)),id=name,name=name,description=oldid)
                SeqIO.write(cds_s, cdsf, "fasta")
                gene_s = SeqRecord(Seq(str(gene_seq.seq)),id=name,name=name,description=oldid)
                SeqIO.write(gene_s, genef, "fasta")
                pep_s = SeqRecord(Seq(str(pep_seq.seq)),id=name,name=name,description=oldid)
                SeqIO.write(pep_s, pepf, "fasta")
                genegff = [row[0],name,str(row[3]),str(row[4]),str(row[6]),str(index+1),oldid]
                gffout.write('\t'.join(genegff)+'\n')
                genecds = gene.drop(gene[(gene[2] != 'CDS') | (gene[10] != pepname)].index)
                for index1,row in genecds.iterrows():
                    cdsgff = [row[0],name,'CDS',str(row[3]),str(row[4]),str(row[5]),str(row[6]),str(row[7]),row[9],row[10]]
                    cdsgffout.write('\t'.join(cdsgff)+'\n')
                geneexon = gene.drop(gene[(gene[2] != 'exon') | (gene[10] != pepname)].index)
                for index1,row in geneexon.iterrows():
                    exonff = [row[0],name,'exon',str(row[3]),str(row[4]),str(row[5]),str(row[6]),str(row[7]),row[9],row[10]]
                    exongffout.write('\t'.join(exonff)+'\n')

        pepf.close()
        cdsf.close()
        genef.close()
        lensf.close()
        gffout.close()
        cdsgffout.close()
        exongffout.close()

    def readncbipep(self):
        print('reading ncbi-pep')
        pep,pepc = {},{}
        for seq_record in SeqIO.parse(self.pep_file, "fasta"):# biopython循环读取
            gene = str(seq_record.description).split()[2]
            if gene not in pepc.keys():
                pepc[gene] = seq_record.id
                pep[seq_record.id] = seq_record
            else:
                if len(seq_record.seq) > len(pep[pepc[gene]].seq):
                    del pep[pepc[gene]]
                    pepc[gene] = seq_record.id
                    pep[pepc[gene]] = seq_record
                elif len(seq_record.seq) == len(pep[pepc[gene]].seq):
                    if seq_record.id < pepc[gene]:
                        del pep[pepc[gene]]
                        pepc[gene] = seq_record.id
                        pep[pepc[gene]] = seq_record
                    else:
                        pass
                else:
                    pass
        print('PEP of number is ',len(pep))
        return pep,pepc

    def readncbicds(self):
        print('reading ncbi-cds')
        cds,cdsc = {},{}
        for seq_record in SeqIO.parse(self.cds_file, "fasta"):# biopython循环读取
            gene = str(seq_record.description).split()[2]
            if gene not in cdsc.keys():
                cdsc[gene] = seq_record.id
                cds[seq_record.id] = seq_record
            else:
                if len(seq_record.seq) > len(cds[cdsc[gene]].seq):
                    del cds[cdsc[gene]]
                    cdsc[gene] = seq_record.id
                    cds[cdsc[gene]] = seq_record
                elif len(seq_record.seq) == len(cds[cdsc[gene]].seq):
                    if seq_record.id < cdsc[gene]:
                        del cds[cdsc[gene]]
                        cdsc[gene] = seq_record.id
                        cds[cdsc[gene]] = seq_record
                    else:
                        pass
                else:
                    pass
        print('CDS of number is ',len(cds))
        return cds,cdsc


    def readncbigene(self,pep,cdsc):
        print('reading ncbi-gene')
        cds = {}
        for seq_record in SeqIO.parse(self.gene_file, "fasta"):# biopython循环读取
            gene = str(seq_record.description).split()[2]
            if seq_record.id in pep:
                cds[seq_record.id] = seq_record
            else:
                cds[cdsc[gene]] = seq_record
        print('gene of number is ',len(cds))
        return cds

    def readncbigenome(self):
        print('reading genome')
        genome = SeqIO.to_dict(SeqIO.parse(self.genome_file, "fasta"))# 提取之后直接返回字典
        print('Chr of number is ',len(genome))
        return genome

    def run(self):
        self.ncbi_gff()
