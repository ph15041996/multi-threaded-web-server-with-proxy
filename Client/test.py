import os
files = ["client.txt"]
for file in files:
    if os.path.exists(file):
        os.remove(file)
    else:
      print("The file does not exist") 
