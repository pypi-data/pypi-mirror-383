# 2025.10.14
import os,math,json,builtins,fileinput,importlib,hashlib,gzip,duckdb,sys, traceback
import pandas as pd
#root1		= os.path.dirname(os.path.abspath(__file__))  #d:\cikuu\mod\yulk\pycode
loadfile	= lambda filename : ''.join(fileinput.input(files=(filename)))

# first run, later can be overwrite macro
for file in [file for _root, dirs, files in os.walk(f"{root}/sql",topdown=False) for file in files if file.endswith(".sql") and not file.startswith("_") ]:
	try:  #'util','yulkinit'
		duckdb.execute(loadfile(f'sql/{file}'))
	except Exception as e:
		print (">>Failed to loadsql:",e, file)
		exc_type, exc_value, exc_obj = sys.exc_info() 	
		traceback.print_tb(exc_obj)

### walk, assuming 'root' exists in builtins
for file in [file for _root, dirs, files in os.walk(f"{root}/park",topdown=False) for file in files if file.endswith(".parquet") and not file.startswith("_") ]:
	name = file.split('.')[0]  # wordlist
	setattr(builtins,name , lambda term, prefix=name: ( duckdb.sql(f"select exists (select * from '{root}/park/{prefix}.parquet' where key = '{term}' limit 1)").fetchone()[0] if not "'" in term else False) if isinstance(term, str) else [ duckdb.sql(f"select exists (select * from '{root}/park/{prefix}.parquet' where key = '{w}' limit 1)").fetchone()[0] for w in term])
	setattr(builtins,f"is{name}", getattr(builtins, name))  # isawl = awl 
	duckdb.sql(f"CREATE or replace MACRO {name}(w) AS ( select exists (select * from '{root}/park/{file}' where key = w limit 1) )")
	duckdb.sql(f"CREATE or replace view {name} AS ( from '{root}/park/{name}.parquet')")

for file in [file for _root, dirs, files in os.walk(f"{root}/parkv",topdown=False) for file in files if file.endswith(".parquet") and not file.startswith("_") ]:
	name = file.split('.')[0]  # idf  
	f	 =  lambda term, prefix=name: (row[0] if not "'" in term and (row:=duckdb.sql(f"select value from '{root}/parkv/{prefix}.parquet' where key = '{term}' limit 1").fetchone()) else None ) if isinstance(term, str) else [ (row[0] if (row:=duckdb.sql(f"select value from '{root}/parkv/{prefix}.parquet' where key = '{w}' limit 1").fetchone()) else None ) for w in term]  # idf(['one','two']) 
	setattr(builtins,name , f)
	duckdb.sql(f"CREATE or replace MACRO {name}(w) AS ( select value from '{root}/parkv/{file}' where key = w limit 1 )")
	duckdb.sql(f"CREATE or replace view {name} AS ( from '{root}/parkv/{name}.parquet')")

for file in [file for _root, dirs, files in os.walk(f"{root}/par",topdown=False) for file in files if file.endswith(".parquet") and not file.startswith("_") ]:
	name = file.split('.')[0]  # first column must be 'key' , ie: ce.parquet 
	duckdb.sql(f"CREATE or replace view {name} AS ( from '{root}/par/{file}' )")
	setattr(builtins,name ,	lambda term, prefix=name: duckdb.sql(f"select * from '{root}/par/{prefix}.parquet' where key = '{term}'").df() if not "'" in term else pd.DataFrame([]) )

for cp in ('en','cn'): 
	duckdb.execute(f"create schema IF NOT EXISTS {cp}")
	setattr(builtins, cp, type(cp, (object,), {'name': cp}) ) # make 'en' as a new class, to attach new attrs later , such en.pos
	x = getattr(builtins, cp) # en.dobjvn('open') -> (label, cnt, keyness)  
	for rel in ('dobjnv','dobjvn','amodan','amodna','advmodvd','advmoddv','advmodad','advmodda','nsubjvn','nsubjnv','conjvv','lempos'): 
		duckdb.execute(f"CREATE OR REPLACE VIEW {cp}.{rel} AS (SELECT key, label, {cp} AS cnt, keyness FROM '{root}/par/{rel}.parquet' WHERE cnt > 0 ORDER BY cnt desc)") #duckdb.execute(f"CREATE OR REPLACE VIEW en.{name} AS (SELECT key, label, en AS cnt, keyness FROM '{root}/par/{name}.parquet' WHERE en > 0 ORDER BY cnt desc)")
		setattr(x, rel, lambda lem, dep=rel,db=cp:  duckdb.sql(f"select label, {db} as cnt, keyness from '{root}/par/{dep}.parquet' where key = '{lem}' and cnt > 0 order by cnt desc").df() if not "'" in lem else pd.DataFrame([]) )
	for name in ('gram2','gram3','gram4','gram5','xgram2','xgram3','xgram4','xgram5','formal','frame','read','snt','svo','termmap','terms','tok','vpat','xtok'):
		if os.path.exists(f"{root}/{cp}/{name}.parquet"): # local version will overwrite the online version
			duckdb.execute(f"create OR REPLACE view {cp}.{name} AS FROM read_parquet('{root}/{cp}/{name}.parquet')")

if __name__ == "__main__": 	pass  
