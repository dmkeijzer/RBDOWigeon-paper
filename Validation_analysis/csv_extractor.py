import pandas as pd
import numpy as np
import os
import sys



class Csv_extractor: #TODO come up with better names lol
    def __init__(self, version, time_stamp):
        self.ml_path = r"C:\Users\damie\OneDrive\Desktop\Damien\Wigeon_proj\logs\valid_data\Monte_Carlo" #Monte Carlo path
        self.bl_path = r"C:\Users\damie\OneDrive\Desktop\Damien\Wigeon_proj\logs\valid_data\Baseline" #Base line path
        
        if version[:2].lower() == "mo":
            folder_lst = os.listdir(self.ml_path)

            for folder in folder_lst:
                if str(time_stamp).replace(":",".") in folder:
                    print(folder)
                    file_lst = os.listdir(os.path.join(self.ml_path, folder))
                    folder_loc = folder
                    break
            for file in file_lst:
                if "csv" in file:  
                    df_output = pd.read_csv(os.path.join(self.ml_path, folder_loc, file))
        
        elif version[:2].lower() == "ba":
            folder_lst = os.listdir(self.bl_path)

            for folder in folder_lst:
                if str(time_stamp).replace(":",".") in folder:
                    file_lst = os.listdir(os.path.join(self.bl_path, folder))
                    folder_loc = folder
                    break
            try:
                for file in file_lst:
                    if "csv" in file:  
                        df_output = pd.read_csv(os.path.join(self.bl_path, folder_loc, file))
            except UnboundLocalError:
                raise Exception(f"Could not find timestamp = {time_stamp}")
            
        else:
            raise OSError(f"Please choose correct folder either baseline or Monte Carlo")
   
        self.df = df_output
            

Analysis_tool = Csv_extractor("baseline", "23:29")

print(Analysis_tool.df)



        