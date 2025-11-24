import re
import os
import shutil

def clean_header_line(line):
    line = line.replace('inc-ttH', '')
    line = line.lstrip('#').strip()
    
    match = re.match(r'(.*?)index\s+(\d+)', line)
    if match:
        var_part, index = match.groups()
        var_clean = re.sub(r'[(),\s]', '', var_part)
        return f"# {var_clean} index {index}"
    return line

# Process all .top files in current directory
for filename in os.listdir('.'):
    if filename.endswith('.top'):
        # Read original content
        with open(filename, 'r') as infile:
            lines = infile.readlines()

        # Prepare cleaned content
        cleaned_lines = []
        for line in lines:
            if line.strip().startswith('#'):
                cleaned_lines.append(clean_header_line(line) + '\n')
            else:
                cleaned_lines.append(line)

        # Backup original file
        backup_filename = filename + '.saved'
        shutil.copy(filename, backup_filename)

        # Overwrite original file with cleaned content
        with open(filename, 'w') as outfile:
            outfile.writelines(cleaned_lines)

        print(f"Processed: {filename} → original saved as {backup_filename}")

        
