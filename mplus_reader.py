#Mplus Output reader too automate summarizing mplus outputs in a folder.

import math
import pandas as pd
import os
import re

#dict containing info to be found and regex to match them
RELEVANT_INFO = {"CatLV": r"Number of categorical latent variables\s*\d+",
				"Parameters": r"Number of Free Parameters\s*\d+",
				"Observations": r"Number of observations\s*\d+",
				"Loglikelihood": r"Loglikelihood\s*H0\s*Value\s*-\d+\.\d+",
				"AIC": r"Akaike\s*\(AIC\)\s*\d+\.*\d+",
				"BIC": r"Bayesian\s*\(BIC\)\s*\d+\.*\d+",
				"ABIC": r"Sample-Size Adjusted BIC\s*\d+\.*\d+",
				"Entropy": r"Entropy\s*\d+\.*\d+",
				"VLMR": r"VUONG-LO-MENDELL-RUBIN LIKELIHOOD RATIO TEST.*P-Value\s*\d+\.*\d+",
				"BLRT": r"PARAMETRIC BOOTSTRAPPED LIKELIHOOD RATIO TEST.*P-Value\s*\d+\.*\d+",
				"Convergence": r"THE BEST LOGLIKELIHOOD VALUE HAS BEEN REPLICATED"
				}

				
Info_for_model_decision = {"CatLV": r"Number of categorical latent variables\s*\d+",
							"ConLV": r"Number of continuous latent variables\s*\d+",
							"MI":	 r"Metric against Configural\s*\d"
							}
					
Info_LPA = {"CatLV": r"Number of categorical latent variables\s*\d+",
			"Observations": r"Number of observations\s*\d+",
			"Parameters": r"Number of Free Parameters\s*\d+",
			"Loglikelihood": r"Loglikelihood\s*H0\s*Value\s*-\d+\.\d+",
			"AIC": r"Akaike\s*\(AIC\)\s*\d+\.*\d+",
			"BIC": r"Bayesian\s*\(BIC\)\s*\d+\.*\d+",
			"ABIC": r"Sample-Size Adjusted BIC\s*\d+\.*\d+",
			"Entropy": r"Entropy\s*\d+\.*\d+",
			"VLMR": r"VUONG-LO-MENDELL-RUBIN LIKELIHOOD RATIO TEST.*P-Value\s*\d+\.*\d+",
			"BLRT": r"PARAMETRIC BOOTSTRAPPED LIKELIHOOD RATIO TEST.*P-Value\s*\d+\.*\d+",
			"Convergence": r"THE BEST LOGLIKELIHOOD VALUE HAS BEEN REPLICATED"
			}

Info_CFA = {"ConLV": r"Number of continuous latent variables\s*\d+",
			"Observations": r"Number of observations\s*\d+",
			"Parameters": r"Number of Free Parameters\s*\d+",
			"CFI": "CFI\D*\d+\.\d+",
			"TLI": "TLI\D*\d+\.\d+",
			"RMSEA": "RMSEA\D*\d+\.\d+",
			"SRMR": "SRMR\D*\d+\.\d+"
			}

Info_MI = {"CFI": r"TLI[ \s]*CFI[ \s]*[\d].[\d]*",
			"RMSEA": "RMSEA\D*\d+\.\d+",
			"SRMR": "SRMR\D*\d+\.\d+"
			}
	


def is_floatable(value):
	try:
		float(value)
		return True
	except:
		return False				
			
			
class MplusOutputSearcher:
	"""Reader object that will hold text and parse it using regex. Takes filename on initialization"""
	def __init__(self, file):

		with open(file) as f:
			self.lines = [line for line in f]
		self.text = " ".join(self.lines)
				
	
	def determine_analysis_type(self):
		"""reads output file and determines whether its a CFA/SEM or LPA Model"""
		CatLV_is_found = self.search_number(re.compile(Info_for_model_decision["CatLV"]))
		ConLV_is_found = self.search_number(re.compile(Info_for_model_decision["ConLV"]))
		MI_is_found = self.search_number(re.compile(Info_for_model_decision["MI"]))
		
		if CatLV_is_found:
			type = "LPA"
			return Info_LPA

		elif MI_is_found or MI_is_found == 0:
			type = "MI"
			return Info_MI
			
		elif ConLV_is_found:
			type = "CFA"
			return Info_CFA
		else:
			print("No latent Variable found")
			
	
	def find_factors_and_indicators(self):
		"""searches the factors and their loadings, to later search for the respective values"""
		pattern = r"(?<=STDYX Standardization)(w*)(?=BY)"
		
	
	def search_number(self, regex_object):
		"""searches for and returns relevant number element in string. returns float if possible,
		if not possible returns string. Takes regex search pattern"""
		regex_search_result = regex_object.search(self.text)
		if regex_search_result:
			string_with_number = regex_search_result.group()
			#reduce string to contain only the number at the end
			only_number = re.compile(r"-?\d+\.*\d*$").search(string_with_number).group()
			#convert to floating point number if possible, else keep it as string
			if is_floatable(only_number):
				only_number = round(float(only_number), 4)
			
			return only_number
			
		else:
			return None
	
	def check_convergence(self, regex_object):
		#TODO: add option to search for convergence in CFAs etc. 
		regex_search_result = regex_object.search(self.text)
		
		if regex_search_result:
			return "Converged"
		else:
			return "Not converged"

	def analyze_MI(self, regex_object):
		numbers = []
		regex_search_result = regex_object.findall(self.text)
		for string in regex_search_result:
			only_number = re.compile(r"\d+\.*\d*$").search(string).group()
			#convert to floating point number
			if is_floatable(only_number):
				only_number = round(float(only_number), 4)
				numbers.append(only_number)
		return numbers
			
			
				
		
			
def calculate_caic(result_dict):
	loglikelihood = result_dict["Loglikelihood"]
	parameters = result_dict["Parameters"]
	N = result_dict["Observations"]
	
	CAIC = -2*loglikelihood + parameters * (math.log(N) + 1)
	return CAIC
	
		
	
	
def main():
	relevant_files = [file for file in os.listdir() if file.endswith(".out")]
	frames = []
	
	for file_index, file in enumerate(relevant_files):
		
		output = MplusOutputSearcher(file)
		result_dict = {"Model Number" : file.strip(".out")}
		
		type_of_analysis = output.determine_analysis_type()

		#if measurement invariance analysis is detected in output 
		if type_of_analysis == Info_MI:
			for item in type_of_analysis:
				results = output.analyze_MI(re.compile(type_of_analysis[item]))
				#add all numbers to output
				
				#add list with the relvant infos for naming the excel output
				model_info = ["configural", "metric", "scalar"]
				for i,number in enumerate(results):
					#name the item ccordingly, i.e. CFI configural
					item_with_model = item + " " + model_info[i]
					result_dict[item_with_model] = number
		
		#for all other analyses
		else:
			for item in type_of_analysis:
				if(item == "Convergence"):
					result = output.check_convergence(re.compile(type_of_analysis[item]))

				else:
					result = output.search_number(re.compile(type_of_analysis[item], re.DOTALL))
						  
				result_dict[item]= result

		if type_of_analysis == Info_LPA:
                        if result_dict["Loglikelihood"]:
                                result_dict["CAIC"] = calculate_caic(result_dict)	
		
		new_df = pd.DataFrame(result_dict, index = [file_index])
		frames.append(new_df)
	
	final_df = pd.concat(frames, sort = False)
	
	#sort LPA/LCA columns in excel file in more convenient order
	if type_of_analysis == Info_LPA:
		final_df = final_df[['Model Number', 'CatLV', 'Observations', 'Parameters',
						'Loglikelihood', 'AIC', 'CAIC', 'BIC', 'ABIC', 'Entropy',
						'VLMR', 'BLRT', 'Convergence']]
	
	final_df.to_excel("output.xlsx")
	
	
	
if __name__ == "__main__":
	main()
