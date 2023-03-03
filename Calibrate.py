#!/usr/bin/env python

from os import path, stat
from sys import exit, argv
from platform import platform

if (platform()[0:7]=="Windows"):
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

class bcolors:
    OKGREEN = '\033[92m'
    OKBLUE = '\033[94m'
    OKPURPLE = '\033[95m'
    INFOYELLOW = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

print(f"{bcolors.OKPURPLE}\n===================")
print("Calibration Started")
print(f"==================={bcolors.ENDC}")

def csvloader(filename):
    print(f"\n[[[ CSV loader: Loading {bcolors.OKBLUE}{filename}{bcolors.ENDC}")
    file=open(f"{filename}","r")
    print(f"Reading file")
    lines=file.readlines()
    flag=0
    count=0
    list1=[]
    i=1
    for line in lines:
        if line[0]!='*':
            line=line.strip('\n')
            line=line.split(',')
            if(len(line)>=2):
                freq=line[0]
                if(line[1][0:1]==" "):
                    amp=line[1][1:]
                else:
                    amp=line[1]
                if(len(list1)==0 or list1[-1][0]<float(freq)):
                    list1.append((float(freq),float(amp)))
                elif(list1[-1][0]==float(freq)):
                    if(count==0):
                        print(f"{bcolors.FAIL}[ {bcolors.ENDC}Two Amplitudes for same Frequency!{bcolors.FAIL} ]{bcolors.ENDC}")
                        print(f"{bcolors.INFOYELLOW}[ {bcolors.ENDC}Using Average for both entries.{bcolors.INFOYELLOW} ]{bcolors.ENDC}")
                        print(f"{bcolors.INFOYELLOW}Check here:{bcolors.ENDC}")
                    count+=1
                    print(f"{count}>    {bcolors.OKBLUE}{list1[-1][0]}{bcolors.INFOYELLOW}:{bcolors.ENDC}{list1[-1][1]} {bcolors.INFOYELLOW}|| {bcolors.OKBLUE}{freq}{bcolors.INFOYELLOW}:{bcolors.ENDC}{amp}")
                    temp=list1[-1][1]
                    list1[-1]=(float(freq),(temp+float(amp))/2)
                elif(list1[-1][0]>float(freq)):
                    print(f"{bcolors.FAIL}[ {bcolors.ENDC}Freq Amp Data not pre-sorted in Ascending order!{bcolors.FAIL} ]{bcolors.ENDC}")
                    print(f"{bcolors.INFOYELLOW}[ {bcolors.ENDC}Sort flag Raised{bcolors.INFOYELLOW} ]{bcolors.ENDC}")
                    print(f"{bcolors.INFOYELLOW}[ {bcolors.ENDC}Data sorting will be done after file loading{bcolors.INFOYELLOW} ]{bcolors.ENDC}")
                    flag=1
                    list1.append((float(freq),float(amp)))
            else:
                print(f"{bcolors.INFOYELLOW}[ {bcolors.ENDC}Skipped {bcolors.OKBLUE}Line {i}{bcolors.ENDC}: Empty or garbage line{bcolors.INFOYELLOW} ]{bcolors.ENDC}")
        else:
            print(f"{bcolors.INFOYELLOW}[ {bcolors.ENDC}Skipped {bcolors.OKBLUE}Line {i}{bcolors.ENDC}: Comment{bcolors.INFOYELLOW} ]{bcolors.ENDC}")
        i+=1
    file.close()
    print(f"File {bcolors.OKBLUE}{filename}{bcolors.ENDC} closed")
    print(f"Total lines read: {bcolors.OKBLUE}{i-1}{bcolors.ENDC}")
    print(f"No. of data entries loaded: {bcolors.OKBLUE}{len(list1)}{bcolors.ENDC}")
    if(flag==1):
        list1=sorted(list1)
        print(f"{bcolors.OKGREEN}[ {bcolors.ENDC}List Sorted{bcolors.OKGREEN} ]{bcolors.ENDC}")
    print(f"{bcolors.OKGREEN}CSV loading done!{bcolors.ENDC} ]]]")
    return list1

def lin_inter(ref, ref_name, slope_gen, slope_name, comlist=[]):
    print("\n[[[ Linear Interpolator starting...")
    print(f"Using {bcolors.OKBLUE}{slope_name}{bcolors.ENDC} as slope generator and {bcolors.OKBLUE}{ref_name}{bcolors.ENDC} as reference")
    comlist2=[]
    list1=[]
    i=0
    j=0
    max_i=len(slope_gen)-1
    max_j=len(ref)-1
    while (i<max_i):
        i+=1
        print(f"{bcolors.OKBLUE}{round(i/max_i*100,2)}%{bcolors.ENDC} {bcolors.INFOYELLOW}Done{bcolors.ENDC}", end='\r')
        y1=slope_gen[i-1][1]
        y2=slope_gen[i][1]
        x1=slope_gen[i-1][0]
        x2=slope_gen[i][0]
        slope=(y2-y1)/(x2-x1)
        while(j<=max_j):
            if (j) in comlist:
                j+=1
                continue
            if(ref[j][0]<x1):
                j+=1
            elif(ref[j][0]==x1):
            	list1.append((ref[j][0],y1))
            	comlist2.append(i-1)
            	j+=1
            elif(ref[j][0]<x2 and ref[j][0]>x1):
                list1.append((ref[j][0],slope*(ref[j][0]-x1)+y1))
                j+=1
            elif(ref[j][0]>=x2):
                break
    if(max_i not in comlist and slope_gen[max_i][0]==ref[max_j][0]):
        list1.append((ref[max_j][0],slope_gen[max_i][1]))
        comlist2.append(max_i)
    print(f"\n{bcolors.OKGREEN}Interpolation complete!{bcolors.ENDC} ]]]")
    return list1, comlist2

def trim(inlist, limitlist, filename):
    print("\n[[[ Trim initiated...")
    i=0
    print("Geting limits...")
    if(not inlist or not limitlist):
        print(f"Input Lists have exact common bins!")
        print(f"Emptying out {bcolors.OKBLUE}{filename}{bcolors.ENDC}")
        print(f"{bcolors.OKGREEN}Trim Complete!{bcolors.ENDC} ]]]")
        return []
    while inlist[i][0]!=limitlist[0][0]:
            i+=1
    print(f"Triming data at start of {bcolors.OKBLUE}{filename}{bcolors.ENDC}")
    while len(inlist)>len(limitlist)+i:
        inlist.pop(-1)
    print(f"Trimming data at end of {bcolors.OKBLUE}{filename}{bcolors.ENDC}")
    while inlist[0][0]!=limitlist[0][0]:
        inlist.pop(0)
    print(f"{bcolors.OKGREEN}Trim Complete!{bcolors.ENDC} ]]]")
    return inlist

if(len(argv)!=4):
    print(f"\n{bcolors.INFOYELLOW}[ {bcolors.ENDC}Please use the following format{bcolors.INFOYELLOW} ]{bcolors.ENDC}")
    print(f"{bcolors.INFOYELLOW}[[{bcolors.ENDC} {argv[0]} {bcolors.INFOYELLOW}<{bcolors.ENDC}Raw_file{bcolors.INFOYELLOW}>{bcolors.ENDC} {bcolors.INFOYELLOW}<{bcolors.ENDC}Reference_file{bcolors.INFOYELLOW}>{bcolors.ENDC} {bcolors.INFOYELLOW}<{bcolors.ENDC}Output_file{bcolors.INFOYELLOW}> ]]{bcolors.ENDC}")
    exit(f"{bcolors.FAIL}[[[ Three arguments are required!! ]]]\n\n=================\nCalibration Exit!\n=================\n{bcolors.ENDC}")

if (path.exists(f"{argv[1]}") and stat(f"{argv[1]}").st_size != 0):
    print(f"\n{bcolors.OKGREEN}[[ {bcolors.ENDC}Path to {bcolors.OKBLUE}{argv[1]}{bcolors.ENDC} located{bcolors.OKGREEN} ]]{bcolors.ENDC}")
    Raw_name=argv[1]
else:
    print(f"\n{bcolors.FAIL}[ {bcolors.ENDC}Error opening {bcolors.OKBLUE}{argv[1]}{bcolors.FAIL}: No Such file or Empty file{bcolors.FAIL} ]{bcolors.ENDC}")
    exit(f"{bcolors.FAIL}[[ Check if file exists or has some data! ]]\n\n=================\nCalibration Exit!\n=================\n{bcolors.ENDC}")

if (path.exists(f"{argv[2]}") and stat(f"{argv[2]}").st_size != 0):
    print(f"\n{bcolors.OKGREEN}[[ {bcolors.ENDC}Path to {bcolors.OKBLUE}{argv[2]}{bcolors.ENDC} located{bcolors.OKGREEN} ]]{bcolors.ENDC}")
    Cal_name=argv[2]
else:
    print(f"\n{bcolors.FAIL}[ {bcolors.ENDC}Error opening {bcolors.OKBLUE}{argv[2]}{bcolors.FAIL}: No Such file or Empty file{bcolors.FAIL} ]{bcolors.ENDC}")
    exit(f"{bcolors.FAIL}[[ Check if file exists or has some data! ]]\n\n=================\nCalibration Exit!\n=================\n{bcolors.ENDC}")

Out_name=argv[3]

Raw_data=csvloader(Raw_name)
Cal_data=csvloader(Cal_name)

Cal_inter,common=lin_inter(Raw_data, Raw_name, Cal_data, Cal_name)
Raw_inter=lin_inter(Cal_data, Cal_name, Raw_data, Raw_name, common)[0]

Raw_data=trim(Raw_data, Cal_inter, Raw_name)+Raw_inter
Cal_data=trim(Cal_data, Raw_inter, Cal_name)+Cal_inter

print("\n[[[ Start Sorting...")
Raw_data=sorted(Raw_data)
print(f"Data from {bcolors.OKBLUE}{Raw_name} {bcolors.OKGREEN}Sorted!{bcolors.ENDC}")
Cal_data=sorted(Cal_data)
print(f"Data from {bcolors.OKBLUE}{Cal_name} {bcolors.OKGREEN}Sorted!{bcolors.ENDC} ]]]")

print(f"\nLF Calibration cutoff at: {bcolors.OKBLUE}{Raw_data[0][0]}{bcolors.ENDC}Hz")
print(f"HF Calibration cutoff at: {bcolors.OKBLUE}{Raw_data[-1][0]}{bcolors.ENDC}Hz")
print(f"{bcolors.INFOYELLOW}[ {bcolors.ENDC}No calibration applied beyond these Ranges, defined by the file having the smaller frequency bandwidth data.{bcolors.INFOYELLOW} ]{bcolors.ENDC}")

i=0
min_val=0
Final_data=[]
print("\n[[[ Calculating calibrated values...") 
while i<len(Raw_data):
    print(f"{bcolors.OKBLUE}{round((i+1)/len(Raw_data)*100,2)}%{bcolors.INFOYELLOW} Done{bcolors.ENDC}", end='\r')
    Final_data.append((Raw_data[i][0],Raw_data[i][1]-Cal_data[i][1]))
    i+=1
print(f"\n{bcolors.OKGREEN}Values Calculated!{bcolors.ENDC} ]]]")
l_limit=-20
buffer=l_limit-min(Final_data)[1]
print(f"\nLower Limit Set:{bcolors.OKBLUE}{l_limit}{bcolors.ENDC}dB")
print(f"{bcolors.INFOYELLOW}-----------{bcolors.ENDC}")
print(f"[[ {bcolors.INFOYELLOW}INFO{bcolors.ENDC}: The lower limit sets the minimum amp value to be output the the calibrated CSV. If this value drops below -20 Room Eq Wizard Ignores it for calibration. ]]")
print(f"\nBuffer Value Set: {bcolors.OKBLUE}{buffer}{bcolors.ENDC}dB")
print(f"{bcolors.INFOYELLOW}------------{bcolors.ENDC}")
print(f"[[ {bcolors.INFOYELLOW}INFO{bcolors.ENDC}: Buffer Value is the number added to calibrated data so that it respects Lower Limit Set. ]]")
print(f"\nFile Output Started to {bcolors.OKBLUE}{Out_name}{bcolors.ENDC}...")
i=0
outfile=open(f"{Out_name}","w")
while i<len(Final_data):
    print(f"{bcolors.OKBLUE}{round((i+1)/len(Final_data)*100,2)}%{bcolors.INFOYELLOW} Done{bcolors.ENDC}", end='\r')
    outfile.write(f"{round(Final_data[i][0],6)}, {round(Final_data[i][1]+buffer,6)}\n")
    i+=1
print(f"\nTotal lines written: {bcolors.OKBLUE}{i}{bcolors.ENDC}")
print(f"{bcolors.OKGREEN}Write Successful{bcolors.ENDC}")
print(f"\n{bcolors.OKGREEN}[[[ {bcolors.ENDC}All processes completed successfully{bcolors.OKGREEN} ]]]{bcolors.ENDC}")
print("The Script will now exit...")
print(f"{bcolors.OKPURPLE}\n=================")
print("Calibration Done!")
print(f"=================\n{bcolors.ENDC}")
