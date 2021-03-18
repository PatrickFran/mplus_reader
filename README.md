# mplus_reader
Reads all Mplus output files in same directory and summarizes most important results in a single excel output file that will be created in the same folder.
You will need to have pandas installed with python 3.73 or higher.

To use the file, simply drag it into the same folder as your Mplus outputs and doubleclick it. It will generate an output file with the most important output information. 
As of now, the script will work best with CFA(with or without measurement invariance)/SEM/LCA/LPA/LTA analyses files. It may work less well/not at all for other types of analysis. 

Common Error: If the output file is open in excel and you try to rerun the script, it will crash. Make sure to close the output file before rerunning. 
