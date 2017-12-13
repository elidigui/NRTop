# -*- coding: utf-8 -*-
"""
Created on Tue Jun 02 18:32:09 2015

@author: Chalopin

This program test all the methods of the stat_pressu module.
"""
import Trace as SMF
import os
import re
import unittest as ut
from filecmp import cmp
import platform as pf
import logging

class TestReadDes(ut.TestCase):
    """ Test  ReadDes methods """

    def setUp(self):
        """ Set test up """
        self.rep_test = ".."+os.sep+"cas"+os.sep+"TestReadDes"
        self.test1 = self.rep_test +os.sep+"test1"+os.sep+"test1.txt"
        self.test2 = self.rep_test +os.sep+"test2"+os.sep+"test2.des"
        self.f1    = self.rep_test +os.sep+"test3"+os.sep+"TA3.csv"

    def test_header_Desfile_2_Array(self):
        """ Test if the function read the header of a .des file """
        a = SMF.ReadCsv(self.test2,48,"\s+")
        a_t = a.Desfile_2_Array()
        self.assertEqual(a_t.keys()[1], "ALIM_EIM",
                         "Don't read the write header")

    def test_value_Desfile_2_Array_1(self):
        """ Test if the function reada value of a .des file """
        a = SMF.ReadCsv(self.test2, 48,"\s+")
        a_t = a.Desfile_2_Array()
        self.assertEqual(a_t["ALIM_EIM"][0].round(decimals=6), 2.0999E-002,
                         "Dont read the right value")

    def test_value_Desfile_2_Array_2(self):
        """ Test if the function read a key of a .csv file """
        df1=SMF.ReadCsv(self.f1,8,";").Desfile_2_Array()
        self.assertEqual(df1.keys()[2], "Cour_H Beam3Z-UP",
                         "Dont read the right key")

    def test_value_Desfile_2_Array_3(self):
        """ Test if the function reada value of a .csv file """
        df1=SMF.ReadCsv(self.f1,8,";").Desfile_2_Array()
        self.assertEqual(df1["Cour_H Beam3Z-UP"][0].round(decimals=9), 0.517860133,
                         "Dont read the right value")
 
    def test_find_line(self):
        """ Test if it find the good line in test2.des"""
        a = SMF.ReadCsv(self.test2,0,"\s+")
        s=  a.find_line(self.test2,"Empty_Category20")
        self.assertEqual(s, 38, "Dont find the write line")

    def tearDown(self):
        """ Reset test """
        pass

class TestCompDataFrames(ut.TestCase):
    """ Test the CompDataFrames Class """
    def setUp(self):
        """ Set test up """
        self.rep_test = ".."+os.sep+"cas"+os.sep+"TestCompDataFrames"
        self.f1 = self.rep_test +os.sep+"Dat"+os.sep+"TA3.csv"
        self.f2 = self.rep_test +os.sep+"Dat_ref"+os.sep+"TA3.csv"
        df1=SMF.ReadCsv(self.f1,8,";").Desfile_2_Array()
        df2=SMF.ReadCsv(self.f2,8,";").Desfile_2_Array()
        self.list_df=[df1,df2]
        self.b=SMF.CompDataFrames(self.list_df)
        self.c3=self.b.diff_pd_2(0.01)

    def test_CompDataFrames_1(self):
        """ Test if the DataFrame of the difference of f1 and f2 are the good one"""
        c2=self.b.diff_pd()
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
        
        df1=SMF.ReadCsv(self.f1,8,";").Desfile_2_Array()
        df2=SMF.ReadCsv(self.f2,8,";").Desfile_2_Array()
        self.list_df=[df1,df2]
        
        self.dest1=self.rep_test
        self.dest1_ref_w=self.rep_test+os.sep+"gra_ref_windows" 
        self.dest1_ref_l=self.rep_test+os.sep+"gra_ref_linux"
        self.dest1_ref_wc=self.rep_test+os.sep+"gra_ref_windows_PCCHALOPIN" 
                
        self.b=SMF.CompDataFrames(self.list_df)
        c2=self.b.diff_pd_2(0.01)
        self.f=self.b.col_diff(c2)

    def test_Plot_2_array(self):
        """ Test if plot file are the same as before"""
        P=SMF.PlotCsv(self.list_f,self.list_df,self.f,self.dest1)
        P.plot_2_array()
        res="Cour_H Beam1X-East.png"
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
        self.C=SMF.CompRep(".csv",self.p1,self.p2)
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
        self.rep_test = ".."+os.sep+"cas"+os.sep+"TestNonReg"
        p1=self.rep_test+os.sep+"Dat"
        p2=self.rep_test+os.sep+"Dat_ref"
        f1=p1+os.sep+"TA3.csv"
        f2=p2+os.sep+"TA3.csv"
        self.lf=[f1,f2]

        self.n=8
        self.s=";"
        self.e=1.e-4
        self.o    =self.rep_test+os.sep+"Comp"
        self.o_ref=self.rep_test+os.sep+"Comp_ref"
        self.x=".csv"
        self.z=""
        self.c="0"

        #Create TA3_1.csv in Comp and plot Cour_H Beam1X-East.png in Comp/gra
        self.NR=SMF.NonReg(self.n,self.s,self.e,self.o,self.x,self.c,self.z)

    def test_NonReg(self):
        """ Test if NonReg reads good inputs"""
        self.assertEqual(self.NR.Nh  ,self.n, "Nheader not readen")
        self.assertEqual(self.NR.sep ,self.s, "Field separator not readen")
        self.assertEqual(self.NR.err ,self.e, "Diff treshold  not readen")
        self.assertEqual(self.NR.dout,self.o, "Output dir not readen ")

    def test_RunNonReg(self):
        """ Test if RunNonReg produce the same results"""
        logging.debug("Diff file:%s and %s"%(self.lf[0],self.lf[1]))
        self.NR.RunNonRegFile(self.lf)
        
        res1="TA3_0.0001.csv"
        f1=self.o+os.sep+res1
        f1_ref=self.o_ref+os.sep+res1
        Test=cmp(f1,f1_ref)
        self.assertTrue(Test,"File %s not the same"%res1)
        
        res1="Cour_H Beam1X-East.png"
        f1=self.o+os.sep+"gra"+os.sep+res1
        
        if pf.system()=="Windows":
            if pf.version()=="6.1.7601":
                f1_ref=self.o_ref+os.sep+"gra_ref_windows_PCCHALOPIN"+os.sep+res1
                comp=cmp(f1,f1_ref)
                self.assertTrue(comp, "Plot created have changed")
            elif pf.processor()=="Intel64 Family 6 Model 30 Stepping 5, GenuineIntel":
                f1_ref=self.o_ref+os.sep+"gra_ref_windows"+os.sep+res1
                comp=cmp(f1,f1_ref)
                self.assertTrue(comp, "Plot created have changed")
            else:
                print("Unknown Systeme")
        elif pf.system()=="Linux":
            f1_ref=self.o_ref+os.sep+"gra_ref_linux"+os.sep+res1
            comp=cmp(f1,f1_ref)
            self.assertTrue(comp, "Plot created have changed")

        else:
            raise ValueError("Nor on Windows nether Linux")
        
        
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
        
        self.f=SMF.ConvToCsv()
        
        
    def testPltToCsv_1(self):
        """ Test if the plt file converted is the same as before"""
        lf=self.f.plt_to_csv(self.f1_in)
        self.f.WriteToFile(lf,self.f1_out)
        self.assertTrue(cmp(self.f1_out,self.f1_ref,"File produced have changed"))
        
    def testSavePltToCsv(self):
        """Test if a csv file is created in a tmp directory and 
        if that file haven't changed"""
        pattern = re.compile( r'tecplot', re.I)
        
        if pattern.match(self.format):
            lf=self.f.SavePltToCsv(self.list_f2)
        self.assertTrue(cmp(lf[0],self.f2_out,"Csv file converted from plt are not the same"))
        self.assertTrue(cmp(lf[1],self.f2_out,"Csv file converted from plt are not the same"))
                
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
        
            
    def testArgsDef_1(self):
        """Test a command line to compare 2 files"""
        res1="TA3_0.0001.csv"
        rep_test1=self.rep_test+os.sep+"testArgsDef_1"
        
        p1=rep_test1+os.sep+"Dat"
        p2=rep_test1+os.sep+"Dat_ref"
        f1=p1+os.sep+"TA3.csv"
        f2=p2+os.sep+"TA3.csv"
        #Create a string like in the command line:
        lf=f1+" "+f2
        
        o    =rep_test1+os.sep+"Comp"
        o_ref=rep_test1+os.sep+"Comp_ref"
        fres    =o    +os.sep+res1
        fres_ref=o_ref+os.sep+res1
        
        arg=["-f",lf,"-l","warning","-o",o]
        a=SMF.Argument(arg)
        args=a.ArgsDef()
        a.SetLog(args)
        logging.info('Started')
        a.ArgsMain(args)
        logging.info('Finished')        
        Test=cmp(fres,fres_ref)
        self.assertTrue(Test,"File %s is not the same as %s"%(fres,fres_ref))
        
    def testArgsDef_2(self):
        """Test a command line to compare 2 files"""
        res1="TA3_0.0001.csv"
        rep_test1=self.rep_test+os.sep+"testArgsDef_2"
        
        p1=rep_test1+os.sep+"Dat"
        p2=rep_test1+os.sep+"Dat_ref"
        #Create a string like in the command line:
        lp=p1+" "+p2
        
        o    =rep_test1+os.sep+"Comp"
        o_ref=rep_test1+os.sep+"Comp_ref"
        fres    =o    +os.sep+res1
        fres_ref=o_ref+os.sep+res1
        
        arg=["-r",lp,"-l","debug","-o",o]
        a=SMF.Argument(arg)
        args=a.ArgsDef()
        a.SetLog(args)
        logging.info('Started')
        a.ArgsMain(args)
        logging.info('Finished')        
        Test=cmp(fres,fres_ref)
        self.assertTrue(Test,"File %s is not the same as %s"%(fres,fres_ref))
        
#def suite():
#    suite = ut.TestSuite()
#    suite.addTest(TestReadDes('test_header_Desfile_2_Array'))
#    suite.addTest(TestReadDes('test_value_Desfile_2_Array'))
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
