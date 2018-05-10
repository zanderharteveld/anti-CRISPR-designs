#!/usr/bin/env python

"""Saturation mutagenesis on three residues of choice."""

import argparse
import numpy as np
import os

def create_parser():
	"""
    	Create a CLI parser.
    	:return: the parser object.
    	"""
    	cli_parser = argparse.ArgumentParser(description="Input arguments to run the saturation mutagenesis.",
    									 epilog="Input arguments for creating submission files to run a saturation mutagenesis locally or on castor. "
										"Parallelization enables to run an exhausitve search of three residues, i.e. 20^3 = 8'000 models. "
										"Note that the the number of residues in combinations is HARD CODED to three only (protection so that you don't "
										"explode the submissions, i.e. example for 4 residues: 20^4 = 160'000 models).",
                                  				formatter_class=argparse.RawDescriptionHelpFormatter)
    	cli_parser.add_argument('--rosetta_scripts_path', '-p', type=str, default='~/bin/Rosetta/main/source/bin/rosetta_scripts.linuxiccrelease', nargs=1, help="Path to Rosettas rosetta_scripts executable and release type (/user/bin/Rosetta/main/source/bin/rosetta_scripts.linuxgccrelease")
	cli_parser.add_argument('--input_structure', '-s', type=str, default=1, nargs=1, help="Input structure.")
	cli_parser.add_argument('--structures', '-nstruct', type=int, default=1, nargs=1, help="Number of outputs for each combination. Default = 1.")
	cli_parser.add_argument('--submission_type', '-sub', type=str, default='castor', nargs=1, help="Run it locally or on castor. Options are 'local' or 'castor'. Default = castor.")
	cli_parser.add_argument('--automatic_submission', '-auto_sub', type=str, default='True', nargs=1, help="Automatically submit everything or just print submission files. Default = true.")
	cli_parser.add_argument('--aa_hotspot_1', '-hot1', type=str, default=1, nargs=1, help="First residue number to mutate with chain identifier.")
	cli_parser.add_argument('--aa_hotspot_2', '-hot2', type=str, default=1, nargs=1, help="Second residue number to mutate with chain identifier.")
	cli_parser.add_argument('--aa_hotspot_3', '-hot3', type=str, default=1, nargs=1, help="Third residue number to mutate with chain identifier.")
	cli_parser.add_argument('--chain', '-chain', type=str, default='A', nargs=1, help="Chain on which residues are mutated. Default A")
	cli_parser.add_argument('--job_arrays', '-j', type=int, default=100, nargs=1, help="Number of arrays / parallel jobs on the cluster. Default = 100")
	return cli_parser

def parse_args(parser):
    	"""
    	Parse the arguments of a parser object.
    	:param parser: the parser object.
    	:return: the specified arguments
    	"""
	args = parser.parse_args()
	return args

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def create_folder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
	print ("Error: Creating directory. {0}".format(directory))	

def main():
    	"""
    	Main execution point. Run the CLI.
   	 """
    	# Parse arguments
    	args = parse_args(create_parser())
    	rosetta_path = args.rosetta_scripts_path[0]
	input_structure = args.input_structure[0]
	submission_type = args.submission_type[0]
	automatic_submission = str2bool(args.automatic_submission[0])
	nstruct = args.structures[0]
	hot1 = args.aa_hotspot_1[0]
	hot2 = args.aa_hotspot_2[0]
	hot3 = args.aa_hotspot_3[0]
	jobs = args.job_arrays[0]

	# Create output directory
	create_folder("./out/")
	
	# Storing all command-lines to submit into a list
	aa_alphabet = ("ALA", "ARG", "ASN", "ASP", "CYS", "GLU", "GLN", "GLY", "HIS", "ILE", "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL")
	#_FLAGS = ""
	_CASTOR_COMMAND_STRING = "srun {0} -s {1} -parser:protocol ../saturation_mutagenesis_minimize.xml -out:file:silent out_${{SLURM_ARRAY_JOB_ID}}_{4}_{6}_{8} -nstruct {2} -ignore_unrecognized_res -ex1 -ex2 -parser:script_vars target1={3} spot1={4} target2={5} spot2={6} target3={7} spot3={8} -out:prefix {4}_{6}_{8}_ -overwrite"
	_LOCAL_COMMAND_STRING = "{0} -s {1} -parser:protocol ../saturation_mutagenesis_minimize.xml -out:file:silent out_{4}_{6}_{8} -nstruct {2} -ignore_unrecognized_res -ex1 -ex2 -parser:script_vars target1={3} spot1={4} target2={5} spot2={6} target3={7} spot3={8} -out:prefix {4}_{6}_{8}_ -overwrite"
	commands = []
	if submission_type == 'castor':
		print("In castor mode!")
	elif submission_type == 'local':
		print("In local mode!")
	for aa1 in aa_alphabet:
		for aa2 in aa_alphabet:
			for aa3 in aa_alphabet:
				if submission_type == 'castor':
					run_command = _CASTOR_COMMAND_STRING.format(rosetta_path, input_structure, nstruct, hot1, aa1, hot2, aa2, hot3, aa3)
				elif submission_type == 'local':
					run_command = _LOCAL_COMMAND_STRING.format(rosetta_path, input_structure, nstruct, hot1, aa1, hot2, aa2, hot3, aa3)
				else:
					print("ERROR: Please check the submission. Allowed options are local or castor.")
				commands.append(run_command)
				#print(run_command)
	
	# Parallelization of the submissions
	_CASTOR_SLURM_STRING = "#!/bin/bash\n#SBATCH --nodes 1\n#SBATCH --ntasks-per-node 1\n#SBATCH --cpus-per-task 1\n#SBATCH --mem 8000\n#SBATCH --time 30:00:00\n#SBATCH --array=1-1\n\n{0}\n"
	threshold = round(float(len(commands))/float(jobs) + 0.49)
	n_sub = 1
	file_tag = 0
	#print(len(commands),jobs)
	#print("threshold", threshold)
	for i,command in enumerate(commands):
		if i != 0 and i%threshold==0:
			n_sub += 1
			file_tag = 0
		#print(i)
		#print(n_sub)
		#print(_CASTOR_SLURM_STRING.format(jobs,command))
		if file_tag == 0:
			if submission_type == 'castor':
				with open("out/submitter.castor.{0}.slurm".format(n_sub), "a") as f:
					f.write(_CASTOR_SLURM_STRING.format(command))
			elif submission_type == 'local':
				pass
				#with open("out/submitter.local.{0}.slurm".format(n_sub), "a") as f:
                                       # f.write("{0}\n".format(command))
			else:
                        	print("ERROR: Please check the submission. Allowed options are local or castor.")
		
		else:
			if submission_type == 'castor':
				with open("out/submitter.castor.{0}.slurm".format(n_sub), "a") as f:
                                	f.write("\n{0}\n".format(command))
			elif submission_type == 'local':
                                with open("out/submitter.local.{0}.slurm".format(n_sub), "a") as f:
                                        f.write("{0}\n".format(command))
		
		if file_tag == 0 and n_sub > 1:
			if submission_type == 'castor':
				with open("out/submitter.castor.{0}.slurm".format(n_sub-1), "a") as f:
                                	f.write("\necho 'CASTOR: RUN FINISHED'\n")
			elif submission_type == 'local':
				with open("out/submitter.local.{0}.slurm".format(n_sub-1), "a") as f:
                                        f.write("\necho 'RUN FINISHED'\n")
		file_tag = 1
	
	# Last step left - submission to castor (if selected)!	
	if automatic_submission == True:
		os.chdir("out/")
		if submission_type == 'castor':
			for i in range(n_sub):
				os.system("sbatch submitter.castor.{0}.slurm".format(i+1))
		elif submission_type == 'local':
			for i in range(n_sub):
                                os.system("bash submitter.local.{0}.slurm".format(i+1))
	else:
		print("Submission files printed only. Nothing submitted.")
	
if __name__ == '__main__':
	main()	
