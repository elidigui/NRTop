# -*- coding: utf-8 -*-
"""
Created on Tue Jun 02 18:32:09 2015

@author: Chalopin

This program test all the methods of the stat_pressu module.
"""
import os
import re
import unittest as ut
from filecmp import cmp
import platform as pf
import logging
import NRTop as NRT
import pandas as pd

class TestReadDes(ut.TestCase):
    """ Test  ReadDes methods """

    def setUp(self):
        """ Set test up """
        self.rep_test = ".."+os.sep+"cas"+os.sep+"TestReadDes"
        self.test1 = self.rep_test +os.sep+"test1"+os.sep+"test1.txt"
        self.test2 = self.rep_test +os.sep+"test2"+os.sep+"test2.des"
        self.f1    = self.rep_test +os.sep+"test3"+os.sep+"TA3.csv"
        self.f2    = self.rep_test +os.sep+"test4"+os.sep+"TA3.csv"

    def test_header_Csvfile_2_Array(self):
        """ Test if the function read the header of a .des file """
        a = NRT.ReadCsv(self.test2,48,"\s+")
        a_t = a.Csvfile_2_Array()
        self.assertEqual(a_t.keys()[1], "ALIM_EIM",
                         "Don't read the write header")

    def test_value_Csvfile_2_Array_1(self):
        """ Test if the function reada value of a .des file """
        a = NRT.ReadCsv(self.test2, 48,"\s+")
        a_t = a.Csvfile_2_Array()
        self.assertEqual(a_t["ALIM_EIM"][0].round(decimals=6), 2.0999E-002,
                         "Dont read the right value")

    def test_value_Csvfile_2_Array_2(self):
        """ Test if the function read a key of a .csv file """
        df1=NRT.ReadCsv(self.f1,8,";").Csvfile_2_Array()
        self.assertEqual(df1.keys()[2], "Cour_H Beam3Z-UP",
                         "Dont read the right key")

    def test_value_Csvfile_2_Array_3(self):
        """ Test if the function reada value of a .csv file """
        df1=NRT.ReadCsv(self.f1,8,";").Csvfile_2_Array()
        self.assertEqual(df1["Cour_H Beam3Z-UP"][0].round(decimals=9), 0.517860133,
                         "Dont read the right value")

    def test_value_Csvfile_2_Array_4(self):
        """ Test if the function reada value of a .csv file """
        df1=NRT.ReadCsv(self.f2,8,",").Csvfile_2_Array()
        self.assertEqual(df1["Cour_H Beam3Z-UP"][0].round(decimals=9), 0.517860133,
                         "Dont read the right value")

   
    def tearDown(self):
        """ Reset test """
        pass

class TestCompDataFrames(ut.TestCase):
    """ Test the CompDataFrames Class """
    def setUp(self):
        """ Set test up """
        self.rep = ".."+os.sep+"cas"+os.sep+"TestCompDataFrames"
        self.rep_test1=self.rep +os.sep+"test_CompDataFrames_123"
        self.f1 = self.rep_test1 +os.sep+"Dat"+os.sep+"TA3.csv"
        self.f2 = self.rep_test1 +os.sep+"Dat_ref"+os.sep+"TA3.csv"
        df1=NRT.ReadCsv(self.f1,8,",").Csvfile_2_Array()
        df2=NRT.ReadCsv(self.f2,8,",").Csvfile_2_Array()
        self.list_df=[df1,df2]
        self.b=NRT.CompDataFrames(self.list_df)
        self.c3=self.b.diff_pd_2(0.01)
        
        self.rep_test2=self.rep +os.sep+"test_CompDataFrames_col_etero"
        self.si={ 'Cour_H Beam1X-East',
                 'Cour_H Beam2Y-North',
                 'Cour_H Beam3Z-UP',
                 'Cour_H PP',
                 'Cour_I Beam1X-East',
                 'Cour_I Beam2Y-North',
                 'Cour_I Beam3Z-UP',
                 'Cour_I PP',
                 'Cour_J Beam1X-East',
                 'Cour_J Beam2Y-North',
                 'Cour_J Beam3Z-UP',
                 'Cour_J PP',
                 'Cour_K Beam1X-East',
                 'Cour_K Beam2Y-North',
                 'Cour_K Beam3Z-UP',
                 'Cour_K PP',
                 'Temps (s)'}
        self.sr={ 'Cour_J PP2' }
        self.f2_1 = self.rep_test2 +os.sep+"Dat"+os.sep+"TA3.csv"
        self.f2_2 = self.rep_test2 +os.sep+"Dat_ref"+os.sep+"TA3.csv"
        
        self.rep_test3=self.rep +os.sep+"test_create_df_with_col_selected_from_set"
        self.f3_1 = self.rep_test3 +os.sep+"Dat"+os.sep+"TA3.csv"
        self.f3_2 = self.rep_test3 +os.sep+"Dat_ref"+os.sep+"TA3.csv"
        self.sref={ 'Cour_H Beam1X-East','Cour_H Beam2Y-North'}
        self.c1=pd.DataFrame()
        self.c2=pd.DataFrame()
        self.c1['Cour_H Beam1X-East']=[-10.000000,-3.464046,-3.138074,-3.197010]
        self.c1['Cour_H Beam2Y-North']=[0.189000,0.200000,0.330119,0.269000]
        self.c2['Cour_H Beam1X-East']=[-3.206309,-3.464046,-3.138074,-3.197010]
        self.c2['Cour_H Beam2Y-North']=[0.189000,0.200000,0.330119,0.269000]
        

    def test_CompDataFrames_1(self):
        """ Test if the DataFrame of the difference of f1 and f2 are the good one"""
        c2=self.b.diff_pd_2(0.01)
        c2_=c2["diff_rel"].values[0]
        self.assertEqual(c2_.round(decimals=6), 0.679369,
                         "Dont read the right value")

    def test_CompDataFrames_2(self):
        """ Test if the diff between f1 and f2 obove 0.1 are the good one"""
        c3_=self.c3["diff_rel"].values[0]
        self.assertEqual(c3_.round(decimals=6), 0.679369,
                         "Dont read the right value")

    def test_CompDataFrames_col_diff(self):
        """ Test if col_diff return the good columnu name """
        f2=self.b.col_diff(self.c3)
        self.assertEqual(f2[0], "Cour_H Beam1X-East", "Dont read the right value")

    def test_CompDataFrames_1(self):
        """ Test if the DataFrame of the difference of f1 and f2 are the good one"""
        c2=self.b.diff_pd_2(0.01)
        c2_=c2["diff_rel"].values[0]
        self.assertEqual(c2_.round(decimals=6), 0.679369,
                         "Dont read the right value")
    
    def test_CompDataFrames_unic_col(self):
        """ Test if the DataFrame of the difference of f1 and f2 are the good one"""
        d1=NRT.ReadCsv(self.f2_1,8,",").Csvfile_2_Array()
        d2=NRT.ReadCsv(self.f2_2,8,",").Csvfile_2_Array()
        b=NRT.CompDataFrames([d1,d2])
        (si,sr)=b.unic_col()
        self.assertTrue(si==self.si,"UnicCol does'nt return right set")
        self.assertTrue(sr==self.sr,"UnicCol does'nt return right set")
    
    def test_create_df_with_col_selected_from_set(self):
        """ Test if a Df is createdfrom a DF with only the 
        column specified in a set sref.
        As the CompDataFrame is used, 2 DF have to be created..."""
        d1=NRT.ReadCsv(self.f3_1,8,",").Csvfile_2_Array()
        d2=NRT.ReadCsv(self.f3_2,8,",").Csvfile_2_Array()
        b=NRT.CompDataFrames([d1,d2])
        
        (d_1,d_2)=b.create_df_with_col_selected_from_set(self.sref)
        n1=self.c1.columns.shape[0]
        n2=self.c2.columns.shape[0]
        n_1=d_1.columns.shape[0]
        n_2=d_2.columns.shape[0]
        self.assertEqual(n1,n_1,"Number of col differ between c1 and d1")
        self.assertEqual(n2,n_2,"Number of col differ between c1 and d1")
        s1=set(d_1.columns)
        s2=set(d_2.columns)
        self.assertEqual(s1,self.sref,"Df1.col != self.sref")
        self.assertEqual(s2,self.sref,"Df2.col != self.sref")
        
    def tearDown(self):
        """ Reset test """
        pass


class TestPlotCsv(ut.TestCase):
    """ Test the PlotCsv Class """

    def setUp(self):
        """ Set test up """
        self.rep_test = ".."+os.sep+"cas"+os.sep+"TestPlotCsv"
        self.f1 = self.rep_test+os.sep+"Dat"+os.sep+"TA3.csv"
        self.f2 = self.rep_test+os.sep+"Dat_ref"+os.sep+"TA3.csv"
        self.list_f=[self.f1,self.f2]

        df1=NRT.ReadCsv(self.f1,8,",").Csvfile_2_Array()
        df2=NRT.ReadCsv(self.f2,8,",").Csvfile_2_Array()
        self.list_df=[df1,df2]

        self.dest1=self.rep_test
        self.dest1_ref_w=self.rep_test+os.sep+"gra_ref_windows" 
        self.dest1_ref_l=self.rep_test+os.sep+"gra_ref_linux"
        self.dest1_ref_wc=self.rep_test+os.sep+"gra_ref_windows_PCCHALOPIN" 

        self.b=NRT.CompDataFrames(self.list_df)
        c2=self.b.diff_pd_2(0.01)
        self.f=self.b.col_diff(c2)
        
        self.frmt1="matplotlib"

    def test_Plot_2_array(self):
        """ Test if plot file are the same as before"""
        P=NRT.PlotCsv(self.list_f,self.list_df,self.f,self.dest1,self.frmt1)
        P.plot_list_of_col()
        res="Cour_H_Beam1X-East.png"
        if pf.system()=="Windows":
            if (pf.version()=="6.1.7601"):
                comp=cmp(self.dest1+os.sep+"gra"+os.sep+res,
                         self.dest1_ref_wc      +os.sep+res)
                self.assertTrue(comp, "Plot created have changed")
            elif pf.processor()=="Intel64 Family 6 Model 30 Stepping 5, GenuineIntel":
                comp=cmp(self.dest1+os.sep+"gra"+os.sep+res,
                         self.dest1_ref_w       +os.sep+res)
                self.assertTrue(comp, "Plot created have changed")
            else:
                print("Unknown Systeme")
        elif pf.system()=="Linux":
            comp=cmp(self.dest1+os.sep+"gra"+os.sep+res,
                     self.dest1_ref_l       +os.sep+res)
            self.assertTrue(comp, "Plot created have changed")

        else:
            raise ValueError("Nor on Windows nether Linux")

    def tearDown(self):
        """ Reset test """
        pass


class TestCompRep(ut.TestCase):
    """ Test the CompRep Class """
    def setUp(self):
        """ Set test  """
        self.rep_test = ".."+os.sep+"cas"+os.sep+"TestCompRep"
        self.p1 = self.rep_test+os.sep+"Dat"
        self.p2 = self.rep_test+os.sep+"Dat_ref"
        self.exp=".csv"
        self.C=NRT.CompRep(".csv",self.p1,self.p2)
        self.L=self.C.FindFilesInDir()

    def test_FindFilesInDir_1(self):
        """ Test if FindFilesInDir finds all .csv files in d1 and d2"""
        self.assertEqual(self.L[0], "TA3.csv", "The file TA3.csv was not found")
        self.assertEqual(self.L[1], "TA3_bis.csv", "The file TA3_bis.csv was not found")

    def test_CompFilesInDir_1(self):
        """ Test if CompFilesInDir keep just files that are different between
        p1 and p2"""
        L2=self.C.CompFilesInDir(self.L)
        self.assertEqual(L2[0], "TA3.csv", "The file TA3.csv was not found")
        self.assertEqual(len(L2), 1, "There is more than 1 element in the list")

    def tearDown(self):
        """ Reset test """
        pass


class TestNonReg(ut.TestCase):
    """ Test the NonReg Class """

    def setUp(self):
        """ Set test  """
        self.rep_tNR = ".."+os.sep+"cas"+os.sep+"TestNonReg"
        self.repNRc= self.rep_tNR+os.sep+"test_config_1"
        self.repNR1= self.rep_tNR+os.sep+"test_NonRegProject_1"
        self.repP1= self.repNR1+os.sep+"TestNonReg1"
        self.repP2= self.repNR1+os.sep+"TestNonReg2"
        self.repD1= self.repP1+os.sep+"Dat"
        self.repD1ref= self.repP1+os.sep+"Dat_ref"
       
        self.n=8 #Number of line to jump in the compared files
        self.s="," #Field separator in the compared files
        self.e=1.e-4 # Relative error treshold
        self.x=".csv" #Compared file's extension
        self.z="0"   # Removing  tmp files created if format=tecplot "1=yes, 0=no"
        self.c="csv" # Format of thhe compared file
        self.o="Comp"

        self.ProjectConfig="config"


    def test_NonReg_init(self):
        """ Test if NonReg reads good inputs"""
        self.NR=NRT.NonReg(self)
        self.assertEqual(self.NR.Nh  ,self.n, "Nheader not readen")
        self.assertEqual(self.NR.sep ,self.s, "Field separator not readen")
        self.assertEqual(self.NR.err ,self.e, "Diff treshold  not readen")
        self.assertEqual(self.NR.dout,self.o, "Output dir not readen ")

    def test_NonRegFile_1(self):
        """ Test if RunNonReg produce the same results"""
        p1=self.repD1
        p2=self.repD1ref

        f1=p1+os.sep+"TA3.csv"
        f2=p2+os.sep+"TA3.csv"
        lf=[f1,f2]
        logging.debug("Diff file:%s and %s"%(lf[0],lf[1]))

        self.o = self.repD1+os.sep+"Comp" #Path to the comparison folder
        o_ok  = self.repD1+os.sep+"Comp_ok" #Path to the comparison folder
        res1="TA3_0.0001.csv"

        #Instantiate a NonReg object with arguments in self:
        self.NR=NRT.NonReg(self)
        #Create TA3_1.csv in Comp and plot Cour_H Beam1X-East.png in Comp/gra
        self.NR.RunNonRegFile(lf)   

        f1=self.o+os.sep+res1
        f1_ok=o_ok+os.sep+res1
        Test=cmp(f1,f1_ok)
        self.assertTrue(Test,"File %s and %s differ"%(f1,f1_ok))

        res1="Cour_H_Beam1X-East.png"
        f1=self.o+os.sep+"gra"+os.sep+res1
        fexist=os.path.isfile(f1)
        self.assertTrue(fexist,"%s does not exist"%f1)
#        if pf.system()=="Windows":
#            if pf.version()=="6.1.7601":
#                f1_ref=o_ok+os.sep+"gra_ref_windows_PCCHALOPIN"+os.sep+res1
#                comp=cmp(f1,f1_ref)
#                self.assertTrue(comp, "Plot created have changed")
#            elif pf.processor()=="Intel64 Family 6 Model 30 Stepping 5, GenuineIntel":
#                f1_ref=o_ok+os.sep+"gra_ref_windows"+os.sep+res1
#                comp=cmp(f1,f1_ref)
#                self.assertTrue(comp, "Plot created have changed")
#            else:
#                print("Unknown Systeme")
#        elif pf.system()=="Linux":
#            f1_ref=o_ok+os.sep+"gra_ref_linux"+os.sep+res1
#            comp=cmp(f1,f1_ref)
#            self.assertTrue(comp, "Plot created have changed")
#        else:
#            raise ValueError("Nor on Windows nether Linux")

    def test_RunNonRegDir_1(self):
        p1=self.repD1
        p2=self.repD1ref
        lp=[p1,p2]
        self.o = self.repP1+os.sep+"Comp" #Path to the comparison folder
        o_ok  = self.repP1+os.sep+"Comp_ok" #Path to the comparison folder
        #Instantiate a NonReg object with arguments in self:
        self.NR=NRT.NonReg(self)
        self.assertEqual(self.NR.dout,self.o, "Output dir not readen ")
        #Create TA3_0.0001.csv in self.o and plot Cour_H Beam1X-East.png in self.o/gra
        self.NR.RunNonRegDir(lp)

        res1="TA3_0.0001.csv"
        f1=self.o+os.sep+res1
        f1_ok=o_ok+os.sep+res1
        logging.debug("File %s and %s are compared:"%(f1,f1_ok))
        Test=cmp(f1,f1_ok)
        self.assertTrue(Test,"File %s and %s differ"%(f1,f1_ok))

    def test_ReadConfigFile_1(self):
        """Test if the config file is readen correctly"""
        #Config file's path:
        fconf=self.repNRc+os.sep+self.ProjectConfig
        #Arguments:
        arg=["-i",fconf,"-l","debug"]
        a=NRT.Argument(arg)
        #Create an args dictionnary with argparse:
        args=a.ArgsDef()
        #Instantiate a NonReg object:
        logging.info('Started')
        NR=NRT.NonReg(args)
        logging.info('Finished')
        #Read the config file of the Non Reg Project:
        conf=NR.ReadConfigFile(args.i[0])

        rep=conf['Project']
        D1=rep[0]['path']+os.sep+rep[0]['DirToComp'][0]
        D2=rep[0]['path']+os.sep+rep[0]['DirToComp'][1]
        D3=rep[1]['path']+os.sep+rep[1]['DirToComp'][0]
        D4=rep[1]['path']+os.sep+rep[1]['DirToComp'][1]
        
        self.assertEqual(os.path.normpath(D1),os.path.normpath(self.repP1+os.sep+"Dat")    ,"Not the good config Proj1's 1st Path")
        self.assertEqual(os.path.normpath(D2),os.path.normpath(self.repP1+os.sep+"Dat_ref"),"Not the good config Proj1's 2nd Path")
        self.assertEqual(os.path.normpath(D3),os.path.normpath(self.repP2+os.sep+"Dat")    ,"Not the good config Proj2's 1st Path")
        self.assertEqual(os.path.normpath(D4),os.path.normpath(self.repP2+os.sep+"Dat_ref"),"Not the good config Proj2's 2nd Path")


    def test_RunNonRegProject_1(self):
        """Test if a project is achived well"""
        #Config file's path:
        fconf=self.repNR1+os.sep+self.ProjectConfig
        #Arguments:
        arg=["-s",",","-i",fconf,"-l","debug"]
        a=NRT.Argument(arg)
        #Create an args dictionnary with argparse:
        args=a.ArgsDef()
        #Instantiate a NonReg object:
        NR=NRT.NonReg(args)
        #Read the config file of the Non Reg Project:
        conf=NR.ReadConfigFile(args.i[0])
        #Launch the project
        logging.info('Started')
        NR.RunNonRegProject(conf)
        logging.info('Finished')

        o  = self.repP1+os.sep+"CompDiff" #Path to the comparison folder
        o_ok  = self.repP1+os.sep+"Comp_ok" #Path to the comparison folder
        res1="TA3_0.0001.csv"
        f1=o+os.sep+res1
        f1_ok=o_ok+os.sep+res1
        logging.debug("File %s and %s are compared:"%(f1,f1_ok))
        Test=cmp(f1,f1_ok)
        self.assertTrue(Test,"File %s and %s differ"%(f1,f1_ok))

        res1="TA4_0.0001.csv"
        f1=o+os.sep+res1
        f1_ok=o_ok+os.sep+res1
        logging.debug("File %s and %s are compared:"%(f1,f1_ok))
        Test=cmp(f1,f1_ok)
        self.assertTrue(Test,"File %s and %s differ"%(f1,f1_ok))

        o  = self.repP2+os.sep+"Comp" #Path to the comparison folder
        o_ok  = self.repP2+os.sep+"Comp_ok" #Path to the comparison folder
        res1="TA3_0.0001.csv"
        f1=o+os.sep+res1
        f1_ok=o_ok+os.sep+res1
        logging.debug("File %s and %s are compared:"%(f1,f1_ok))
        Test=cmp(f1,f1_ok)
        self.assertTrue(Test,"File %s and %s differ"%(f1,f1_ok))

        res1="TA4_0.0001.csv"
        f1=o+os.sep+res1
        f1_ok=o_ok+os.sep+res1
        logging.debug("File %s and %s are compared:"%(f1,f1_ok))
        Test=cmp(f1,f1_ok)
        self.assertTrue(Test,"File %s and %s differ"%(f1,f1_ok))

#    def testCleanTmp_1(self):
#        """Test if the tmp dir hav not been removed when z=0"""
#        p1=self.repD1
#        p2=self.repD1ref
#
#        f1=p1+os.sep+"TA3.csv"
#        f2=p2+os.sep+"TA3.csv"
#        lf=[f1,f2]
#        logging.debug("Diff file:%s and %s"%(lf[0],lf[1]))
#
#        self.o = self.repD1+os.sep+"Comp" #Path to the comparison folder
#        o_ok  = self.repD1+os.sep+"Comp_ok" #Path to the comparison folder
#        res1="TA3_0.0001.csv"
#
#        #Instantiate a NonReg object with arguments in self:
#        self.NR=NRT.NonReg(self)
#        #Create TA3_1.csv in Comp and plot Cour_H Beam1X-East.png in Comp/gra
#        self.NR.RunNonRegFile(lf)   
#
#        tmp1 = p1+os.sep+os.sep+tmp
#        ftmp1 = tmp1+os.sep+"TA3.csv"
#        os.path.isdir(tmp1)
#        self.assertTrue(os.path.isdir(tmp1),"tmp%s doesn't exist"%tmp1)
#        self.assertTrue(os.path.isfile(ftmp1),"File %s doesn't exist"%ftmp1)
#    
    
    def tearDown(self):
        """ Reset test """
        #os.remove(self.o)
        pass


class TestConToCsv(ut.TestCase):
    """ Test the ConvToCsv Class """
    def setUp(self):
        """ Set test  """
        self.rep_test = ".."+os.sep+"cas"+os.sep+"TestConvToCsv"
        self.f1_in =self.rep_test+os.sep+"testPltToCsv"+os.sep+"testPltToCsv_1.plt"
        self.f1_ref=self.rep_test+os.sep+"testPltToCsv"+os.sep+"testPltToCsv_1_ref.csv"
        self.f1_out=self.rep_test+os.sep+"testPltToCsv"+os.sep+"testPltToCsv_1.csv"

        self.format="tecplot"
        self.f2_in =self.rep_test+os.sep+"testSavePltToCsv"+os.sep+"testPltToCsv_1.plt"
        self.f2_ref=self.rep_test+os.sep+"testSavePltToCsv"+os.sep+"testPltToCsv_1_ref.csv"
        self.f2_out=self.rep_test+os.sep+"testSavePltToCsv"+os.sep+"tmp"+os.sep+"testPltToCsv_1.csv"
        self.list_f2=[self.f2_in,self.f2_in]

        self.f3_in =self.rep_test+os.sep+"testDesToCsv"+os.sep+"test2.des"
        self.f3_ref=self.rep_test+os.sep+"testDesToCsv"+os.sep+"test2_ref.csv"
        self.f3_out=self.rep_test+os.sep+"testDesToCsv"+os.sep+"test2.csv"
        
        self.f4_in =self.rep_test+os.sep+"testNhToCsv"+os.sep+"test2.des"
        self.f4_ref=self.rep_test+os.sep+"testNhToCsv"+os.sep+"test2_ref.csv"
        self.f4_out=self.rep_test+os.sep+"testNhToCsv"+os.sep+"tmp"+os.sep+"test2.csv"
        self.list_f4=[self.f4_in,self.f4_in]
        self.Nh=53
        

        self.f=NRT.ConvToCsv()

        self.rep_test = ".."+os.sep+"cas"+os.sep+"TestReadDes"
        self.test1 = self.rep_test +os.sep+"test1"+os.sep+"test1.txt"
        self.test2 = self.rep_test +os.sep+"test2"+os.sep+"test2.des"
 
    def test_find_line(self):
        """ Test if it find the good line in test2.des"""
        a = NRT.ConvToCsv()
        s=  a.find_line(self.test2,"Empty_Category20")
        self.assertEqual(s, 38, "Dont find the write line")
    
    def testPltToCsv_1(self):
        """ Test if the plt file converted is the same as before"""
        self.f.plt_to_csv(self.f1_in,self.f1_out)
        self.assertTrue(cmp(self.f1_out,self.f1_ref,"File produced have changed"))

    def testSaveToCsv(self):
        """Test if a csv file is created in a tmp directory and 
        if that file haven't changed"""
        pattern = re.compile( r'tecplot', re.I)

        if pattern.match(self.format):
            lf=self.f.SaveToCsv(self.list_f2,frmt=self.format,Nh=0)
        self.assertTrue(cmp(lf[0],self.f2_out,"Csv file converted from plt are not the same"))
        self.assertTrue(cmp(lf[1],self.f2_out,"Csv file converted from plt are not the same"))

    def testSaveToCsv_2(self):
        """Test if a csv file is created in a tmp directory when arg.Nh>0"""
        lf=self.f.SaveToCsv(self.list_f4,Nh=self.Nh,frmt="")
        self.assertTrue(cmp(lf[0],self.f4_out,"Csv file converted from plt are not the same"))
        self.assertTrue(cmp(lf[1],self.f4_out,"Csv file converted from plt are not the same"))
        
    def test_des_to_csv(self):
        """Test if a des file is correctly converted in csv file."""
        self.f.des_to_csv(self.f3_in,self.f3_out)
        self.assertTrue(cmp(self.f3_out,self.f3_ref,"File produced have changed"))

    def testCleanTmp_1(self):
        """Test if the tmp dir have been removed when c=1"""
        pass

    def testCleanTmp_2(self):
        """Test if the tmp dir have been removed when there is no c (default)"""
        pass

    def testCleanTmp_3(self):
        """Test if the tmp dir have been kept when c=0"""
        pass

    def tearDown(self):
        """ Reset test """
        pass

class TestArgument(ut.TestCase):
    """Test class Argument"""

    def setUp(self):
        """ Init class"""
        self.rep_test = ".."+os.sep+"cas"+os.sep+"TestArgument"
        self.res1="TA3_0.0001.csv"

    def testArgsDef_1(self):
        """Test a command line to compare 2 files"""
        rep_test1=self.rep_test+os.sep+"testArgsDef_1"

        p1 = rep_test1+os.sep+"Dat"
        p2 = rep_test1+os.sep+"Dat_ref"
        f1 = p1+os.sep+"TA3.csv"
        f2 = p2+os.sep+"TA3.csv"
        #Create a string like in the command line:
        lf=f1+" "+f2

        o    =rep_test1+os.sep+"Comp"
        o_ref=rep_test1+os.sep+"Comp_ref"
        fres    =o    +os.sep+self.res1
        fres_ref=o_ref+os.sep+self.res1

        arg=["-f",lf,"-l","warning","-o",o,"-s",","]
        a=NRT.Argument(arg)
        args=a.ArgsDef()
        a.SetLog(args)
        logging.info('Started')
        a.ArgsMain(args)
        logging.info('Finished')        
        Test=cmp(fres,fres_ref)
        self.assertTrue(Test,"File %s is not the same as %s"%(fres,fres_ref))

    def testArgsDef_2(self):
        """Test a command line to compare 2 files"""
        rep_test1=self.rep_test+os.sep+"testArgsDef_2"

        p1=rep_test1+os.sep+"Dat"
        p2=rep_test1+os.sep+"Dat_ref"
        #Create a string like in the command line:
        lp=p1+" "+p2

        o    =rep_test1+os.sep+"Comp"
        o_ref=rep_test1+os.sep+"Comp_ref"
        fres    =o    +os.sep+self.res1
        fres_ref=o_ref+os.sep+self.res1

        arg=["-g",lp,"-l","debug","-o",o,"-s",","]
        a=NRT.Argument(arg)
        args=a.ArgsDef()
        a.SetLog(args)
        logging.info('Started')
        a.ArgsMain(args)
        logging.info('Finished')        
        Test=cmp(fres,fres_ref)
        self.assertTrue(Test,"File %s is not the same as %s"%(fres,fres_ref))


        #def suite():
#    suite = ut.TestSuite()
#    suite.addTest(TestReadDes('test_header_Csvfile_2_Array'))
#    suite.addTest(TestReadDes('test_value_Csvfile_2_Array'))
#    return suite

#List of TestSuites:
suite=[]
suite.append(ut.TestLoader().loadTestsFromTestCase(TestReadDes))
suite.append(ut.TestLoader().loadTestsFromTestCase(TestCompDataFrames))
suite.append(ut.TestLoader().loadTestsFromTestCase(TestPlotCsv))
suite.append(ut.TestLoader().loadTestsFromTestCase(TestCompRep))
suite.append(ut.TestLoader().loadTestsFromTestCase(TestNonReg))
suite.append(ut.TestLoader().loadTestsFromTestCase(TestConToCsv))
suite.append(ut.TestLoader().loadTestsFromTestCase(TestArgument))

alltests = ut.TestSuite(suite)
#suite2 = ut.TestLoader().loadTestsFromTestCase(TestToolDes)
#alltests = ut.TestSuite([suite1, suite2])

#Execution of tests:
for suite_ in alltests:
    ut.TextTestRunner(verbosity=2).run(suite_)

if __name__ == '__main__':
    ut.main()
