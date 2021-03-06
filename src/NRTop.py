# coding: utf-8
#Ouvre le fichier et le nombre de ligne d'entête à sauter en argument
#Saute les entête
#trace toutes les colonnes

import pandas as pd
import numpy as np
import sys #for parsing args
import os
import re
import matplotlib.pyplot as plt
import argparse
import errno
from filecmp import cmp
import logging
import json

def mkrep(rep):
    #Name of the dir where csv file is going to be saved:
    try:
        os.mkdir(rep)
    except OSError as e:       
        if e.errno == errno.EEXIST and os.path.isdir(rep):
            pass
        else:
            raise

class ReadCsv:
    """ Read a csv file with a header and the name of the variable in a row"""

    def __init__(self, filename, Nheader, sep):
        #  Name of the filemane to parse:
        self.fn = filename
        #  Number of header's lines:
        self.Nh = Nheader
        # field separator:
        self.sep = sep
        #pd DataFrame from csvfile:
        self.df=self.to_df()
        
        
    def to_df(self):
        """ Convert a csv file to a pandas dataframe """
        # print("FFFFFFFFFFFFFF f=",self.fn)
        a = pd.read_csv(self.fn, sep = self.sep, encoding = "utf8", header= self.Nh )
        # print("aaaaaaaaaaaaaa.col[0]=",a.columns[0])
        return(a)


class CompDataFrames:
    """ Compare two DataFrames """
    def __init__(self, list_df):
        #  Name of the DataFrames to compare:
        self.df1 = list_df[0]
        self.df2 = list_df[1]

    def diff_rel_pd(self,a1,a2):
        """Calculate the relative difference of each terms of 2 arrays"""
        #a=(a1 - a2)/a1
        a = []
        for i,n in enumerate(a1):
            a.append((float(a1[i])-float(a2[i]))/float(a1[i]))
        return(a)

    def diff_pd_2(self,err):
        """Identify differences between two pandas DataFrames
        Calculate the relative error between elements that are different
        Select those wich are greater than the error criteria err """
        
        # Test if columns are the same:
        if (self.df1.columns.shape[0] != self.df2.columns.shape[0]):
            # Create the set of column names that are in common between 
            #self.df1 and self.df2
            si,sr=self.unic_col()
            for i in sr:
                #♦print("col that are alone=",i)
                logging.info("Columns %s not in both files"%i)
            # Create two DF that have the same collumns """
            (df1,df2)=self.create_df_with_col_selected_from_set(si)
            # print("1df1.columns.shape[0]=",df1.columns.shape[0])
            # print("df2.columns.shape[0]=",df2.columns.shape[0])
            
        else:
            df1 = self.df1
            df2 = self.df2
            # print("2df1.columns.shape[0]=",df1.columns.shape[0])
            # print("df2.columns.shape[0]=",df2.columns.shape[0])
            
        df=pd.DataFrame
        #For files that have the same column names:
        if (df1.columns == df2.columns).all():
            # print("3df1.columns.shape[0]=",df1.columns.shape[0])
            # print("df2.columns.shape[0]=",df2.columns.shape[0])
            if df1.equals(df2):
                #No Diff
                logging.debug("No diff")
                return None
            else:
                #Diff
                logging.debug("Diff")
                # need to account for np.nan != np.nan returning True*$
                #print(df1,df2)
                #logging.debug('df1=%s; df2=%s'%(df1,df2))        
                logging.debug('Finished')        
                #diff_mask = (df1 != df2) & ((df1-df2)/df1 >err) # & ~(df1.isnull() & df2.isnull())
                diff_mask = df1.ne(df2)  & ((df1-df2)/df1 >err) # & ~(df1.isnull() & df2.isnull())
                ne_stacked = diff_mask.stack()
                changed = ne_stacked[ne_stacked]
                changed.index.names = ['id', 'col']
                difference_locations = np.where(diff_mask)
                abscisse = df1.values[difference_locations[0],0]
                #print("diff loc=",difference_locations,"abs=",abscisse)
                changed_from = df1.values[difference_locations]
                changed_to = df2.values[difference_locations]
                diff_rel = self.diff_rel_pd(changed_from,changed_to)
                return(df({'abs':abscisse,
                                      'from': changed_from,
                                      'to': changed_to,
                                      'diff_rel':diff_rel},
                                      index=changed.index))
        else:
            print("4df1.columns.shape[0]=",df1.columns.shape[0])
            print("df2.columns.shape[0]=",df2.columns.shape[0])
            logging.error("df1.columns != df2.columns??")
            return None
            
    def unic_col(self):
        """ Return columns that are common in the two DataFrame d1 and d2"""
        l1=[]
        for i in self.df1.columns:
            l1.append(i)
        s1=set(l1)
        l2=[]
        for i in self.df2.columns:
            l2.append(i)
        s2=set(l2)
        s_intrsct=s1.intersection(s2)
        s_rest=s2.union(s1)-s_intrsct
        return(s_intrsct,s_rest)
        
    def create_df_with_col_selected_from_set(self,s):
        """ Create two DF that have the same collumns """
        df_1=pd.DataFrame()
        for i in s:
            df_1[i]=self.df1[i]
        df_2=pd.DataFrame()
        for i in s:
            df_2[i]=self.df2[i]
        return(df_1,df_2)

    def col_diff(self,c2):
        """" c2 is the DataFrame that result of diff_pd_2(self,err)
        It is treated so that a list of the column names that fit to 
        the error criteria are returned""" 
        #Reset the diff DataFrame so it does'nt have multiple index and 
        #select the relative error column:
        d2 = c2.reset_index().col
        #Create the set of the column names so there is no dobble elements:
        e2 = set(d2)
        #Create a list with that set
        f2 = sorted(e2)
        return(f2)
    
    def egalise_row(self,d1,d2):
        """ Delete last row of the longuer DF so that it have the same
        length than the shorter """
        l1=d1.shape[0]
        l2=d2.shape[0]
        dl=l1-l2
        if dl>0:
            for i in 1,d1:
                d=d1.drop(d1.tail(1).index)
                d1=d
        else:
            for i in 1,-d1:
                d=d2.drop(d2.tail(1).index)
                d2=d
        return(d1,d2)

    def Export_diff(self,d,dest):
        """ Export the result of diff_pd_2 in a csv file """
        d.to_csv(dest,encoding="utf8",sep=";")


class PlotCsv:
    """ Plot panda DataFrames in a dir. gra in the dir. "dest"""
    def __init__(self,list_f,list_df,lcol,dest,PltFrmt): 
        #Name of the files to compare:
        self.f1  = list_f[0]
        self.f2  = list_f[1]
        #Name of the DataFrames to compare:
        self.df1  = list_df[0]
        self.df2  = list_df[1]
        #List of the column name to plot:
        self.lcol = lcol
        #Plot Format:
        self.PlotFormat=PltFrmt
        #Name of the common abscisse:
        self.t    = self.df1.keys()[0]
        self.title =  "1:%s vs\n 2:%s"%(self.f1,self.f2)
        #print self.title
        self.dest = dest+os.sep+"gra"
        mkrep(self.dest)
        logging.debug("Dir. %s created"%self.dest)

    def plot_list_of_col(self):
        """ Plot a list of 2 arrays with matplotlib """
        for col in self.lcol:
            if self.PlotFormat == "matplotlib":
                self.plot_mtpltlib(col)
            elif self.PlotFormat == "gnuplot":
                self.plot_gnuplot(col)

    def plot_mtpltlib(self,col):
        """ Plot 2 arrays with matplotlib """
        plt.title(self.title,fontsize = 8)
        plt.xlabel(self.t)
        plt.ylabel(col)
        plt.plot(self.df1[self.t],self.df1[col],color = 'r',label = "1")
        plt.plot(self.df2[self.t],self.df2[col],color = 'b',label = "2")
        plt.legend(loc = 0)
        plt.grid(color = 'gray', linestyle = '--', linewidth = 0.5)
        nom_fig = self.dest+os.sep+col.replace(" ","_")+".png"
        logging.debug("File %s created"%nom_fig)
        plt.savefig(nom_fig,format = "png")
        plt.close()

    def plot_gnuplot(self,col):
        """ Plot 2 arrays with gnuplot
            Use a template, adapte it, use it to save a png plot 
            and save it or not """
        pass
#        gtmp=self.load_template("gnuplot")    
#        gtmp.replace("__title__",self.title)
#        gtmp.replace("__x__",self.t)
#        gtmp.replace("__y__",col)
#        gtmp.replace("path1",self.f1)
#        gtmp.replace("path2",self.f2)
#        nom_fig = self.dest+os.sep+col.replace(" ","_")
#        nfig_bitmap=nom_fig+".png"
#        nfig_gnuplot=nom_fig+".gp"
#        gtmp.replace("__nomfig__",nfig_bitmap)
#        self.save_template(gtmp,nfig_gnuplot)
#        self.exec_template("gnuplot",nfig_gnuplot)


    def load_template(self):
        pass

    def save_template(self,tmp,f):
        pass

    def exec_template(self,app,f):
        pass

      
class CompRep:
    """ Compare csv files that have the same name in two directories """

    def __init__(self, exp, d1, d2):
        #  Name of the directories to compare:
        self.d1 = d1
        self.d2 = d2
        self.Path = [self.d1, self.d2]
        #Expression to match files in directories:
        self.exp= exp

    def FindFilesInDir(self):
        """ List all the file matching a regexp in a directories
        dir1 and dir2. Return the intersection between those 2 lists"""
        l1 = []
        l2 = []
        L = [l1,l2]
        
        for i,li in  enumerate(L):
            #baselevel = len(os.curdir.split(os.sep))
            for path_,subdirs_,files_ in os.walk(self.Path[i]):
                #curlevel = len(path_.split(os.sep))
                #print("curlevel=", curlevel)
                #if curlevel <= baselevel + 1:
                del subdirs_[:]
                for j,fj in enumerate(files_):
                    # In the first level:
                    if (re.search(self.exp,fj)):
                        li.append(fj)
                        # print("i=",i," li=",li)
        Lf = sorted(set(l1).intersection(l2))
        return(Lf)

    def CompFilesInDir(self, L):
        """ Compare file in L and return those that have the same name 
        and that are different"""
        L_ = []
        #print(L)
        for fi in L:
            # print(u"héhéhé:",self.Path[0]+os.sep+fi,self.Path[1]+os.sep+fi)
            if cmp(self.Path[0]+os.sep+fi,self.Path[1]+os.sep+fi):
                # print("hahaha:",self.Path[0]+os.sep+fi,self.Path[1]+os.sep+fi,":same")
                pass
            else:
                # print(self.Path[0]+os.sep+fi,self.Path[1]+os.sep+fi,":diff")
                L_.append(fi)
        logging.debug("List of file to compare:")
        for i in L_:
            logging.debug("   -%s"%i)
        return(L_)


class NonReg:
    """ Tool to achive a non regression study """
    #NR=NonReg(args.n,args.s,args.e,args.o,args.x,args.c,args.z)
    def __init__(self,args):
        #  Number of line to skip before the one line header of the csv file:
        self.Nh  = args.n
        # Input file's field separator:
        self.sep = args.s
        # Input clean csv file's field separator:
        self.sep2 = args.u
        # Treshold to select column (variable) that duiffer significantly:
        self.err = args.e
        # Directory where diff.csv and Plots will be saved:
        self.dout =  args.o
        # String that match input files that are checked for the NR:
        self.exp = args.x
        # Format of input files (csv (default),tecplot):
        self.format = args.c
        # Cleanup:
        self.clean = args.z
        # PlotFormat:
        self.PlotFormat = "matplotlib"

    def ReadConfigFile(self,inputfile):
        """ Read the file containing the directories of the Non Regression
        project """
        #conf={}
        #print(conf)
        with open(inputfile,'r') as conf_file:    
            conf=json.load(conf_file,encoding="utf-8") 
        return(conf)

#    def JsonRightEncoding(self,response_json):
#        struct = {}
#        try:
#            response_json = str(response_json).strip("'<>() ").replace('\'', '\"')
#            response_json = response_json.decode('utf-8').replace('\0', '')
#            struct = json.loads(response_json)
#        except:
#            print('bad json: ', response_json)
#        return struct

#    def CheckFile(self):
#        """ Check if files of a Directories exist """
#        pass

    def RunNonRegProject(self,conf):
        """ Run a RunNonReg for each directory listed in the Project file """
        for rep in conf["Project"]:
            l=[rep["path"]+os.sep+rep["DirToComp"][0],
               rep["path"]+os.sep+rep["DirToComp"][1]]
            logging.debug("RunNonRegProject")
            #print("l=",l)
            if rep["DirOut"]:
                self.dout=rep["DirOut"]
            else:
                self.dout=rep["path"]+os.sep+"Comp"
            self.RunNonRegDir(l)

    def RunNonRegDir(self,list_d):
        """ Compare file in 2 dirs 2 by 2 ,
            create a diff.csv and 
            plot graphs if the relative difference is greater than a treshold"""
        
        # TODO: WARN if the two dir are not find
        
        #Instantiate CompRep:
        logging.info("Directories %s and %s are compared:"%(list_d[0],list_d[1]))
        C = CompRep(self.exp,list_d[0],list_d[1])
        #List file in dirs that fit the same name:
        L = C.FindFilesInDir()
        #List file in L that are differents:
        L2 = C.CompFilesInDir(L)
        for fi in L2:
            #Create the path to those files
            fi_1 = list_d[0]+os.sep+fi
            fi_2 = list_d[1]+os.sep+fi
            logging.debug("File %s and %s are compared:"%(fi_1,fi_2))
            list_f = [fi_1,fi_2]
            #Create a diff and plot:
            self.RunNonRegFile(list_f)

    def RunNonRegFile(self,list_f):
        """ Compare 2 files, create a diff.csv and a plot graphs if
        the relative difference is greater than a treshold"""

        #Patern that match tecplot whatever is its case
        pat = re.compile( r'tecplot|des', re.I)
        #pat_DES = re.compile( r'des', re.I)
        if (pat.match(str(self.format))):
            #| pat_DES.match(str(self.format)):
            f=ConvToCsv()
            list_f = f.SaveToCsv_frmt(list_f,frmt=self.format,Nh=0, sep2=self.sep2)
            df1 = ReadCsv(list_f[0],0,self.sep2).df
            # print("1-df1.col[0]=",df1.columns[0])
            df2 = ReadCsv(list_f[1],0,self.sep2).df
        elif self.Nh>=0:
            f=ConvToCsv()
            # print("22222222.list_f[0]=%s, nh=%d, sep=%s, sep2=%s"%(list_f[0],self.Nh,self.sep, self.sep2))
            list_f = f.SaveToCsv(list_f,Nh=self.Nh, sep=self.sep, sep2=self.sep2)
            df1 = ReadCsv(list_f[0],0,self.sep2).df
            # print("2-df1.col[0]=",df1.columns[0])
            df2 = ReadCsv(list_f[1],0,self.sep2).df
            # print("DF&.col[0]=",df1.columns[0])
        else:
            logging.error("ERROR args have no -c (file format)  and no -n?=> STOP")
            
        list_df = [df1,df2]

        #Create 2 DataFrames from the 2 files to compare:
        b = CompDataFrames(list_df)

        #Compute differences between 2 DataFrames:
        c2 = b.diff_pd_2(self.err).sort_index(level="col")
        f = os.path.basename(list_f[0])[:-4]
        if c2.empty:
            logging.info("No diff from %s"%f)
        else:
            #Create the Comparation directory if it doesn't exist:
            mkrep(self.dout)
            #Export the result in a csv file:
            fout = f+"_"+str(int(-np.log10(self.err)))+".csv"
            dest=self.dout+os.sep+fout
            logging.debug("Diff file:%s"%dest)
            b.Export_diff(c2,dest)
            #Compute the list of column (variable) that differe:
            f2 = b.col_diff(c2)

            #TODO: Create a table with the max relative diff only for the f2 table 

            #Plot graph comparing the variable of the 2 files:
            P = PlotCsv(list_f,list_df,f2,self.dout,self.PlotFormat)
            P.plot_list_of_col()

        #remove tmp directory contains temporary csv files:
        if pat.match(str(self.format)):
            c = ConvToCsv()
            c.CleanTmp(self.clean,list_f)
#        elif  self.Nh>0:
#            c = ConvToCsv()
#            c.CleanTmp(self.clean,list_f)


class ConvToCsv():
    """Tool for converting file f to simple csv format"""
    def __init__(self):
        pass

    def find_line(self,fi,reg):
        """ Return the number of the line of file fi that first match the 
        regexp reg
        """
        id = reg
        regexp=re.compile(id)
        j = 1
        with open(fi) as f:
            for i,line in enumerate(f):
                if (regexp.search(line)==None):
                    pass
                else:
                    j = j+i
                    break
        return(j)

    def plt_to_csv(self,f,fo,sep2):
        """Convert a Tecplot 2D datafile into a basic 1 header csv file into a
        list object"""
        #List of keyword at the begining of lines to be removes:
        re_param = re.compile(r'^TITLE|ZONE|AUXDATA')
        #Keyword at the begining of lines with variables:
        re_var = re.compile(r'^VARIABLES')

        lfout = []
        with open (f, 'r') as fopen:
            for line in fopen.readlines():
                if not re_param.match(line):
                    if re_var.match(line):
                        #Remove VARIABLES = from the matchin lines:
                        line = re.sub("VARIABLES.*=","",line)
                        #Remove space at the beginning and the end of the line:
                        line = line.strip()
                        #Substitute the " " sequences with sep2:
                        v_ = re.sub('" *"',sep2,line)
                        # Remove the last '"':
                        line = re.sub('"','',v_)
                        # Remove multiple spaces:
                        line = re.sub(' +','',line)
                        lfout.append(line)
                    else:
                        #Remove space at the beginning and the end of the line:
                        line = line.strip()
                        # Remove multiple spaces:
                        line = re.sub(' +',sep2,line)
                        lfout.append(line)
        # print("f1ffffffffffffo=",fo," lo[0]=",lfout[0])
        self.WriteToFile(lfout,fo)

    def des_to_csv(self,f,fo,sep2):
        """Convert a .des file (ModeFrontier result file)  into a basic 1 header csv file into a
        list object"""
        # Find line with variables:
        nh=  self.find_line(f,'<ID>   <RID>')
        # Strip Nh first lines:
        l=self.Nh_to_csv(f,nh)
        lo=[]
        for i,line in enumerate(l):
            if i == 0:
                l_=re.sub('<RID>','',line)
                lo.append(re.sub(' +',sep2,l_))
            else:
                l_=re.sub('\[\]','',line)
                lo.append(re.sub(' +',sep2,l_))
        # print("f2ffffffffffffo=",fo," lo[0]=",lo[0])
        self.WriteToFile(lo,fo)
    
    def clean_csv(self,f,fo,Nh,sep,sep2):
        """Convert a file with a field separator sep to a file with a FS sep2
           substitute all spaces by a _ """
        # Find line with variables:
        # Strip Nh first lines:
        l=self.Nh_to_csv(f,Nh)
        lo=[]
        for line in l:
            # print("lllllllllllllll=",line)
            l_ = re.sub(sep,sep2,line)
            lo.append(re.sub(' +','_',l_))
        # print("f3ffffffffffffo=",fo,"sep=",sep,"sep2=",sep2)
        # print(" lo[0]=",lo[0])
        self.WriteToFile(lo,fo)
        
    #def Nh_to_csv(self,f,fo,Nh):
    def Nh_to_csv(self,f,Nh):
        """Ignore Nh first line,
           convert multiple spaces into sep,
           write the file into a list"""
        lfout = []
        i=0
        with open(f, 'r') as fopen:
        #with open(f, 'r', encoding="latin1") as fopen:
        #with open (f, 'r', encoding="utf8") as fopen:
            for line in fopen.readlines():
                i+=1
                if i < Nh:
                    pass
                else:
                    #Remove space at the beginning and the end of the line:
                    line = line.strip()
                    lfout.append(line)
        return(lfout)
        
    def tmp_csv_file_name(self,fi,tmp_rep):
        """ Create a tmp csv file name and it's path from the 
        original file name """
        rep_tmp = os.path.dirname(fi)+os.sep+tmp_rep
        fo_name = os.path.basename(fi)[:-4]+".csv"
        fo = rep_tmp+os.sep+fo_name
        return(fo,rep_tmp)
    
    def SaveToCsv_frmt(self,list_f,**kwargs):
        """Convert the 2 plt files in list_f into csv file and save it
            in a tmp dir by the plt file"""
        pat_TEC = re.compile( r'tecplot', re.I)
        pat_DES = re.compile( r'des', re.I)
        l_tmp = []
        for i,fi in enumerate(list_f):
            #Name of the dir where csv file is going to be saved:
            fo,rep_tmp = self.tmp_csv_file_name(fi,"tmp")
            l_tmp.append(fo)
            
            #list containing the data tecplot input file converted in csv.
            if pat_TEC.match(str(kwargs['frmt'])):
                # Create Dir if it doesn't exists:
                mkrep(rep_tmp)
                self.plt_to_csv(fi,fo,str(kwargs['sep2']))
            elif pat_DES.match(str(kwargs['frmt'])):
                # Create Dir if it doesn't exists:
                mkrep(rep_tmp)
                self.des_to_csv(fi,fo,str(kwargs['sep2']))
            else:
                logging.debug('format %s not modified'%kwargs['frmt'])
        return(l_tmp)
    
    def SaveToCsv(self,list_f,**kwargs):
        """Convert the 2 files in list_f into liste of csv files"""
        l_tmp = []
        for i,fi in enumerate(list_f):
            #Name of the dir where csv file is going to be saved:
            fo,rep_tmp = self.tmp_csv_file_name(fi,"tmp")
            l_tmp.append(fo)
            
            # Create Dir if it doesn't exists:
            mkrep(rep_tmp)
            self.clean_csv(fi,fo,float(kwargs['Nh']),str(kwargs['sep']),str(kwargs['sep2']))
            logging.info('file %s cleaned and saved in %s'%(fi,fo))
        return(l_tmp)

    def WriteToFile(self,lf,f_out):
        """ Write a list into a file """
        with open (f_out, 'w') as fp:
            #print("hello","\n".join(lf))
            fp.write("\n".join(lf))

    def CleanTmp(self,c,list_f):
        """Remove tmp directory contains temporary csv files"""
        if c == 1:
            for i,fi in enumerate(list_f):
                fo,rep_tmp = self.tmp_csv_file_name(fi,"tmp")
                os.remove(rep_tmp)
                logging.debug('Dir. %s removed'%rep_tmp)
        else:
            for i,fi in enumerate(list_f):
                fo,rep_tmp = self.tmp_csv_file_name(fi,"tmp")
                logging.info("File %s have been created"%fo)


class Argument():
    """Group all arguments"""

    def __init__(self,l):
        """ Init class"""
        #Argument list:
        self.larg = l
        pass

    def ArgsDef(self):
        """ Return arguments in distinct variables"""
        parser = argparse.ArgumentParser(description='Compare plots of two series of result to chec the non regression')
        parser.add_argument('t'                               ,type = str  ,nargs = '+', default = 'f',\
                            help = '(f file1 file2 (Path of 2 files to compare)) || \
                                    (g path1 path2 (Paths of the 2 rep of files to compare)) || \
                                    (i path_t_config_file (Paths to the  config file)),\
                                    default=f file1 file2')
        parser.add_argument('-o','--out'           ,dest = 'o',type = str  ,nargs = '?',default = 'Comp',help = 'Directory where to save graphs and comparison file')
        parser.add_argument('-e','--err'           ,dest = 'e',type = float,nargs = '?',default = 1e-4,  help = 'Relative difference above wich it is taken into account')
        parser.add_argument('-s','--FieldSeparator',dest = 's',type = str  ,nargs = '?',default = ";",   help = 'Field Separator in the readen files')
        parser.add_argument('-u','--CsvFieldSeparator',dest = 'u',type = str  ,nargs = '?',default = ";",   help = 'Field Separator in the readen files converted in clean csv file')
        parser.add_argument('-n','--NHeader'       ,dest = 'n',type = int  ,nargs = '?',default = 0,     help = 'Number of line to skip before the one line header of the csv file')
        parser.add_argument('-x','--Research'      ,dest = 'x',type = str  ,nargs = '?',default=".*"   ,help = 'Regexp that match with compared file name')
        parser.add_argument('-c','--ConvertedFormat',dest = 'c',type = str ,nargs = '?'               ,help = 'Type of file format to be converted in csv. Accepted: Tecplot, des')
        parser.add_argument('-z','--clean'         ,dest = 'z',type = str  ,nargs = '?',default = 1     ,help = 'Clean files converted in csv format in the tmp dir.: 1: clean (Default), 0: keep')
        parser.add_argument('-l','--logging'       ,dest = 'l',type = str  ,nargs = '?',default = "WARNING"  ,help = 'Log info: DEBUG, INFO, WARNING (default), ERROR, CRITICAL')

    #def ParseArgs(self):
        args = parser.parse_args(self.larg)
        return(args)

    def SetLog(self,args):
        """ Set logging function """
        #Log level:
        numeric_level = getattr(logging, args.l.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % args.l)
        logging.basicConfig(filename='NRTop.log',
                filemode='w',format='%(levelname)s; %(asctime)s; %(message)s',
                level=numeric_level)
        #logging.basicConfig(filename='NRTop.log', filemode='w',format='%(levelname)s; %(asctime)s; %(message)s', level=logging.DEBUG)
        #logging.basicConfig(                                    format='%(levelname)s; %(asctime)s; %(message)s', level=numeric_level)

    def ArgsMain(self,args):
        #create the comparison directory:
        try:
            os.mkdir(args.o)
        except OSError as e:       
            if e.errno == errno.EEXIST and os.path.isdir(args.o):
                pass
            else:
                raise

#        #Check the consistancy of the arguments:
#        if(args.c):
#            if (args.x == "csv"):
#                raise ValueError("args.x=csv or args.c=tecplot (or des) but not both")
#            elif(args.n):
#                if(args.n==0):
#                    if (args.z==1):
#                       raise ValueError("No csv file are going to be created so clean have to be 0")     
#                    else:
#                        print("Conversion of file format is done in tmp dirs")    
#                else:
#                    raise ValueError("if args.c is not empty, no header is going to be deleted")
#               


        #print(args.t[1:])
        #Run the comparison:
        NR=NonReg(args)
        if args.t[0]=="f":
            """ Comparison of two files """
            list_f=args.t[1:]
            # print("list_f=",list_f)
            NR.RunNonRegFile(list_f)
        elif args.t[0]=="g":
            #print(args.t[1:])
            """Comparison of two directories"""
            list_d=args.t[1:]
            NR.RunNonRegDir(list_d)
        elif args.t[0]=="i":
            conf=NR.ReadConfigFile(args.t[1])
            NR.RunNonRegProject(conf)

if __name__ == '__main__':
    #Lecture des arguments:
    a=Argument(sys.argv[1:])
    #Reads and record argument in variables (sys.args). 
    #args=a.ArgsDef(sys.argv[1:]) #[1:] avoid the 2 first éelements ("python"
    #and "NRTop.py") that are in the command line
    args=a.ArgsDef()
    a.SetLog(args)
    logging.info('Started')
    a.ArgsMain(args)

    logging.info('Finished')        

   # list_var2=args.list_var[0].split()
    # print("Variable to be treated:")
    # for i in list_var2:
        # print("  "+i)
    # print("Directory where file will be save:"+args.rep_out)
    # print("Type of file to be created:"+args.to_csv)
    # t=ToolDes()
    # if args.to_csv=='histogram':
        # if args.LimDict!='':
            # print(u"Limits from file ",args.LimDict,u" will be ploted")
            # LimDict=t.Creat_LimDist(args.LimDict)
            # print(LimDict)
            # t.trace_hist(list_f_in2,list_var2,args.rep_out,LD=LimDict)
        # else:
            # t.trace_hist(list_f_in2,list_var2,args.rep_out)
    # elif args.to_csv=='csv file':
        # t.cree_tab(list_f_in2,list_var2,args.rep_out)
    # else:
        # print("Neither histogram nor csv file")
