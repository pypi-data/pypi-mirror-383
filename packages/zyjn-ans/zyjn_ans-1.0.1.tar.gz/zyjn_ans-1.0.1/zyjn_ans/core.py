import os
import pkg_resources

# Define the menu
menu = """Available Codes:
1. Model4.py - Smart Home System
2. task1_1_ans.py - Camera and Image Processing  
3. task1_2_ans.py - Video Processing and Text Analysis
4. task2.py - Shape Recognition CNN Training
5. task2_ans.py - Shape Recognition CNN (Alternative)
6. task3_ans.py - RKNN Model and Object Detection"""

# Load code files
def _load_code_files():
    code_files = {}
    for i in range(1, 7):
        file_path = pkg_resources.resource_filename('zyjn_ans', f'data/code{i}.py')
        with open(file_path, 'r', encoding='utf-8') as f:
            code_files[i] = f.read()
    return code_files

# File dictionary
file = _load_code_files()

# Save function
def save(code_content, filename=None):
    """
    Save code content to current directory
    
    Args:
        code_content: The code content to save (from file dictionary)
        filename: Optional filename, will use default if not provided
    """
    if filename is None:
        # Extract filename from code content if possible
        lines = code_content.split('\n')
        for line in lines:
            if line.startswith('[file name]:'):
                filename = line.split(':')[1].strip()
                break
        if filename is None:
            filename = "saved_code.py"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code_content)
    
    print(f"Code saved to: {filename}")