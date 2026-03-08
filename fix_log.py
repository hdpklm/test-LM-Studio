import os

try:
    with open('project_log.md', 'rb') as f:
        data = f.read()
    print("Read bytes:", len(data))
    
    # Let's find out if there are zero bytes or invalid utf-8
    decoded = data.decode('utf-8', errors='replace')
    
    # Save a fixed copy 
    with open('project_log_fixed.md', 'w', encoding='utf-8') as f:
        f.write(decoded)
    print("Fixed file saved.")
except Exception as e:
    print("Error:", e)
