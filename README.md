# 📌 AIDA Installation Guide  

This project contains a plugin developed for **IDA Pro 9.1**. Follow the steps below to complete the installation.  

## 🚀 Installation Steps  

### 1️⃣ Install Required Dependencies  
After downloading the source code, install the necessary Python libraries by running the following command:  

```bash
pip install -r requirements.txt
```  

⚠ **Important:** Install the dependencies directly in the global Python environment, **not in a virtual environment (venv).**  

### 2️⃣ Copy Plugin Files  
Once the dependencies are installed, copy the entire plugin folder to the following directory:  

```
C:\Program Files\IDA Professional 9.1\plugins
```  

### 3️⃣ Configure Python Interpreter (If Needed)  
If you have multiple versions of Python installed on your system, you may need to update the Python interpreter used by IDA.  

To do this, check the `README_python3.txt` file located in the **IDA installation directory** and follow the instructions to set the correct Python version.  

## 🎯 How to Use  

After completing the installation:  

1. Open **IDA Pro**.  
2. Open any function in **Pseudocode View** (by pressing `F5`).  
3. Right-click anywhere in the pseudocode window and click the **"Summarize"** button.  

🛑 **If the "Summarize" button is missing, the plugin was not installed correctly.**  

If you encounter any issues, feel free to contact me through the **Discord link on my profile**.  
