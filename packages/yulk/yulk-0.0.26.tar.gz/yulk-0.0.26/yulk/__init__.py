# 2025.10.14
import requests,os,math,json,builtins,hashlib,duckdb,warnings
import pandas as pd
import marimo as mo
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt

builtins.duckdb = duckdb
builtins.pd		= pd
builtins.json	= json
builtins.os		= os
builtins.root	= os.path.dirname(os.path.abspath(__file__)) #os.path.dirname(yulk.__file__)
builtins.requests = requests
builtins.mo		= mo
builtins.px		= px
builtins.plt	= plt
builtins.alt	= alt
warnings.filterwarnings("ignore")

### walk pycode/*.py,   loadsql in pycode/walk.py 
for file in [file for _root, dirs, files in os.walk(f"{root}/pycode",topdown=False) for file in files if file.endswith(".py") and not file.startswith("_") ]:
	try:
		name = file.split('.')[0]  
		mod = getattr( __import__('pycode.'  + name), name) #  __import__('os')  =  import os,  only keep functions,   skip global variable ,  builtins.kvr must be set manually 
		[ setattr(builtins, name, getattr(mod, name)) for name in dir(mod) if not name.startswith("_")  and callable( getattr(mod, name) )] # overwrite the former
	except Exception as e:
		print ("load pycode ex:", name, e, flush=True) 

#[setattr(builtins, k, f) for k, f in globals().items() if not k.startswith("_") and not '.' in k and not hasattr(builtins,k) and callable(f) ]
if __name__ == "__main__": 	
	pass  
