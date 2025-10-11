# 2025.10.10
import requests,os,math,json,builtins,zlib,fileinput,importlib,hashlib,gzip,duckdb,warnings
import pandas as pd
builtins.duckdb = duckdb
builtins.pd		= pd
builtins.json	= json
builtins.os		= os
builtins.root	= os.path.dirname(os.path.abspath(__file__)) #os.path.dirname(yulk.__file__)
builtins.requests = requests
warnings.filterwarnings("ignore")

sntmd5			= lambda text: hashlib.md5(text.strip().encode("utf-8")).hexdigest() #000003fa-c0b1-5d48-5490-ef083f787596
module_exists	= lambda module_name='cikuu.mod.attrdict': importlib.util.find_spec(module_name) is not None
json.get		= lambda cmd, **kwargs :requests.get( f"http://{kwargs.get('host','yulk.net')}/{cmd}").json()  # json.get('pos~book'), return a json 
dobjvn			= lambda key, **kwargs: pd.DataFrame( requests.get( f"http://{kwargs.get('host','yulk.net')}/dobjvn('{key}',cp='{kwargs.get('cp','en')}')").json() ) #http://yulk.net/dobjvn('book',cp='cn')
lempos			= lambda key, **kwargs: pd.DataFrame( requests.get( f"http://{kwargs.get('host','yulk.net')}/lempos('{key}',cp='{kwargs.get('cp','en')}')").json() )
checkin			= lambda: [setattr(builtins, k, f) for k, f in globals().items() if not k.startswith("_") and not '.' in k and not hasattr(builtins,k) and callable(f) ]
sntdf			= lambda snt: pd.DataFrame( requests.get(f'http://yulk.net/parse~{snt}').json()) # snt -> df 
sql				= lambda q: duckdb.sql(q).fetchdf()
loadsql			= lambda name: duckdb.execute(requests.get(f'http://file.yulk.net/sql/{name}.sql').text)

def loadpy(name):  ## load duck/yulk..., from pyexec/*.py 
	try:
		dic = {}
		compiled_code = compile(requests.get(f'http://file.yulk.net/py/{name}.py').text, f"{name}.py", 'exec') 
		exec(compiled_code,dic)
		[setattr(builtins, name, obj) for name, obj in dic.items() if not name.startswith("_") and not '.' in name and callable(obj)] # latter will overwrite former : and not hasattr(builtins,name)
	except Exception as e:
		print ("loadpy ex:", name, e, flush=True) 
	return pd.DataFrame([{"name":name, 'obj':str(obj)} for name, obj in dic.items() if not name.startswith("_") and callable(obj)])

def walkline(infile): 
	for id, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): 
		yield ( id, str(line,'utf-8') if isinstance(line, bytes) else line )
fileinput.walk = walkline 

### walk
for file in [file for _root, dirs, files in os.walk(f"{root}/park",topdown=False) for file in files if file.endswith(".parquet") and not file.startswith("_") ]:
	name = file.split('.')[0]  # wordlist
	setattr(builtins,name , lambda term, prefix=name: ( duckdb.sql(f"select exists (select * from '{root}/park/{prefix}.parquet' where k = '{term}' limit 1)").fetchone()[0]) if isinstance(term, str) else [ duckdb.sql(f"select exists (select * from '{root}/park/{prefix}.parquet' where k = '{w}' limit 1)").fetchone()[0] for w in term])
	setattr(builtins,f"is{name}", getattr(builtins, name))  # isawl = awl 
	duckdb.sql(f"CREATE or replace MACRO {name}(w) AS ( select exists (select * from '{root}/park/{file}' where k = w limit 1) )")

for file in [file for _root, dirs, files in os.walk(f"{root}/parkv",topdown=False) for file in files if file.endswith(".parquet") and not file.startswith("_") ]:
	name = file.split('.')[0]  # idf  |  vec = lambda term: ( res:=duckdb.sql(f"select v from '/yulk/parkv/vec.parquet' where k = '{term}' limit 1").fetchone() if not "'" in term else None, res[0] if res else [])[-1] 
	f	 =  lambda term, prefix=name: (row[0] if (row:=duckdb.sql(f"select v from '{root}/parkv/{prefix}.parquet' where k = '{term}' limit 1").fetchone()) else None ) if isinstance(term, str) else [ (row[0] if (row:=duckdb.sql(f"select v from '{root}/parkv/{prefix}.parquet' where k = '{w}' limit 1").fetchone()) else None ) for w in term]  # idf(['one','two']) 
	setattr(builtins,name , f)
	duckdb.sql(f"CREATE or replace MACRO {name}(w) AS ( select v from '{root}/parkv/{file}' where k = w limit 1 )")
	duckdb.sql(f"CREATE or replace view {name} AS ( from '{root}/parkv/{name}.parquet')")

for file in [file for _root, dirs, files in os.walk(f"{root}/par",topdown=False) for file in files if file.endswith(".parquet") and not file.startswith("_") ]:
	name = file.split('.')[0]  # first column must be 'key' , ie: ce.parquet 
	duckdb.sql(f"CREATE or replace view {name} AS ( from '{root}/par/{file}' )")
	setattr(builtins,name ,	lambda term, prefix=name: duckdb.sql(f"select * from '{root}/par/{prefix}.parquet' where key = '{term}'").df() )

def parse(snt): 
	import spacy
	if not hasattr(parse, 'nlp') : setattr(parse, 'nlp',  spacy.load(os.getenv('spacy_model','en_core_web_sm') ) )  
	return parse.nlp(snt)
def snts(text:str="She has ready. It are ok."): 
	import spacy
	from spacy.lang import en
	if not hasattr(sntbr, 'inst'):
		sntbr.inst = en.English()
		sntbr.inst.add_pipe("sentencizer")
	doc		= sntbr.inst(text)
	return  [ sp.text.strip() for i,sp in enumerate(doc.sents) ] 

ROOT = lambda snt: next(iter([ t.lemma_ for t in parse(snt) if t.dep_ == 'ROOT']), None) #next(iter(lst), None)
tc	 = lambda snt: len(snt.split())
np	 = lambda snt: [ np.text for np in parse(snt).noun_chunks]
wget		= lambda filename, **kwargs:	requests.get(f"http://{kwargs.get('host','file.yulk.net')}/{kwargs.get('folder','py')}/{filename}").text
wgetjson	= lambda filename, **kwargs:	requests.get(f"http://{kwargs.get('host','file.yulk.net')}/{kwargs.get('folder','json')}/{filename}").json()
jsongz		= lambda name:	json.loads(zlib.decompress(requests.get(f'http://file.yulk.net/json/{name}.json.gz').content, 16 + zlib.MAX_WBITS).decode('utf-8')) 

def cache(name): 
	if not hasattr(cache, name):  # wgetjson('stop.json') 
		dic = wgetjson(name) if '.' in name else jsongz(name)
		if name.endswith('set'): dic = set(dic)  # stopset, awlset 
		setattr(cache, name, dic)
	return getattr( cache, name)
stopset		= lambda word:	word in cache('stopset') if isinstance(word, str) else [ stopset(w) for w in word] 
awlset		= lambda word:	word in cache('awlset') if isinstance(word, str) else [ awlset(w) for w in word] 
wordidf		= lambda word:	cache('wordidf').get(word, 0) if isinstance(word, str) else [ wordidf(w) for w in word]  # pandas.core.series.Series
#lemlex		= lambda word:	cache('lemlex').get(word, word) if isinstance(word, str) else [ lemlex(w) for w in word] 
duckdb.create_function('stopset', stopset , [str], bool)
duckdb.create_function('awlset', awlset , [str], bool)
duckdb.create_function('wordidf', wordidf , [str], float)
#duckdb.create_function('lemlex', lemlex , [str], str)
duckdb.execute("create view ce as (from read_parquet('http://file.yulk.net/par/ce.parquet'))")
duckdb.execute("create view c as (from read_parquet('http://file.yulk.net/par/c.parquet'))")
duckdb.execute("create view e as (from read_parquet('http://file.yulk.net/par/e.parquet'))")

def loglike(a,b,c,d):  #from: http://ucrel.lancs.ac.uk/llwizard.html
	from math import log as ln
	try:
		if a is None or a <= 0 : a = 0.000001
		if b is None or b <= 0 : b = 0.000001
		if c is None or c <= 0 : c = 0.000001
		if d is None or d <= 0 : d = 0.000001
		E1 = c * (a + b) / (c + d)
		E2 = d * (a + b) / (c + d)
		G2 = round(2 * ((a * ln(a / E1)) + (b * ln(b / E2))), 2)
		if (a * d < b * c): G2 = 0 - G2 #if minus or  (minus is None and a/c < b/d): G2 = 0 - G2
		return round(G2,1)
	except Exception as e:
		print ("likelihood ex:",e, a,b,c,d)
		return 0
duckdb.create_function("loglike", loglike, [int,int,int,int], float)

def keyness(df1, df2, **kwargs): 
	src		= {row[0]: int(row[1]) for index, row in df1.iterrows()} if hasattr(df1, 'iterrows') else {row[0]: int(row[1]) for row in df1.iter_rows()} # <class 'polars.dataframe.frame.DataFrame'> of sql
	tgt		= {row[0]: int(row[1]) for index, row in df2.iterrows()} if hasattr(df2, 'iterrows') else {row[0]: int(row[1]) for row in df2.iter_rows()}
	sum1	= src.get("_sum", sum( [i for s,i in src.items()]) ) + 0.000001 # read from attrs 
	sum2	= tgt.get("_sum", sum( [i for s,i in tgt.items()]) ) + 0.000001
	words	= src.keys() if 'leftonly' in kwargs else set( list(src.keys()) + list(tgt.keys()) )
	rows	= [ (w, round(100*src.get(w,0)/sum1,2), round(100*tgt.get(w,0)/sum2,2), src.get(w,0), tgt.get(w,0), loglike(src.get(w,0), tgt.get(w,0), sum1, sum2 )) for w in words if not w.startswith('_sum') ] #_look forward to _VBG
	rows.sort(key=lambda row:row[-1], reverse='asc' in kwargs) 
	return pd.DataFrame(rows, columns=['field','src%', 'tgt%', 'src','tgt', 'keyness']) #[('two', 72.0, 15, 0, 123, 1233), ('three', -23.8, 0, 125, 123, 1233), ('one', -0.0, 12, 123, 123, 1233)]

def save_gz(file_path, content=""): #save_gz("a.txt.gz", "hello world")
	import gzip
	from pathlib import Path
	path = Path(file_path)
	path.parent.mkdir(parents=True, exist_ok=True) # create if needed
	with gzip.open(path, 'wt', encoding='utf-8') as f:
		f.write(content)
	return path

def load_jsongz(file_path):
	with gzip.open(file_path, 'rt', encoding='utf-8') as f:
		data = json.load(f)
	return data # already a dict

[setattr(builtins, k, f) for k, f in globals().items() if not k.startswith("_") and not '.' in k and not hasattr(builtins,k) and callable(f) ]
if __name__ == "__main__": 
	pass  
