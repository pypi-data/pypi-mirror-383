# 2025.10.14, cp from api.py 
import requests,os,math,itertools,duckdb,zlib,json
import pandas as pd

sql			= lambda q: duckdb.sql(q).fetchdf()
gramcnt		= lambda gram: ( res:=duckdb.sql(f"select value from read_parquet('http://file.yulk.net/yulk/parkv/gramcnt.parquet') where key ='{gram}' limit 1").fetchone() if not "'" in gram else None, res[0] if res else None)[-1] if isinstance(gram, str) else [ gramcnt(s) for s in gram]
parkv		= lambda name, k: ( res:=duckdb.sql(f'''select value from read_parquet('http://file.yulk.net/parkv/{name}.parquet') where key ='{k.replace("'","''")}' limit 1''').fetchone(), res[0] if res else None)[-1] if isinstance(k, str) else [ parkv(name,s) for s in k]
park		= lambda name, k: ( res:=duckdb.sql(f'''select exists (from read_parquet('http://file.yulk.net/park/{name}.parquet') where key ='{k.replace("'","''")}' limit 1)''').fetchone(), res[0] if res else None)[-1] if isinstance(k, str) else [ park(name,s) for s in k]
par			= lambda name, k: duckdb.sql(f'''from read_parquet('http://file.yulk.net/par/{name}.parquet') where key ='{k.replace("'","''")}' ''').fetchdf()
parlike		= lambda name, k: duckdb.sql(f'''from read_parquet('http://file.yulk.net/par/{name}.parquet') where key like '{k.replace("'","''")}%' ''').fetchdf()

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
duckdb.create_function('stopset', stopset , [str], bool)
duckdb.create_function('awlset', awlset , [str], bool)
duckdb.create_function('wordidf', wordidf , [str], float)

if os.path.exists(f"{root}/par/ce.parquet"):
	duckdb.execute("create OR REPLACE view ce as (from read_parquet('{root}/par/ce.parquet'))")
	duckdb.execute("create OR REPLACE view c as (select key, label, cn as cnt from read_parquet('{root}/par/ce.parquet') where cnt > 0 order by cnt desc)")
	duckdb.execute("create OR REPLACE view e as (select key, label, en as cnt from read_parquet('{root}/par/ce.parquet') where cnt > 0 order by cnt desc)")
else: 
	duckdb.execute("create OR REPLACE view ce as (from read_parquet('http://file.yulk.net/yulk/par/ce.parquet'))")
	duckdb.execute("create OR REPLACE view c as (from read_parquet('http://file.yulk.net/yulk/par/c.parquet'))")
	duckdb.execute("create OR REPLACE view e as (from read_parquet('http://file.yulk.net/yulk/par/e.parquet'))")

def bncsum(): # assume: bnc function exists 
	if not hasattr(bncsum, 'sum'): bncsum.sum = bnc('_sum') 
	return bncsum.sum
logbnc	= lambda word, wordcnt, wordsum: likelihood(wordcnt, bnc(word), wordsum, bncsum()) # * tup, or a row 
duckdb.create_function('logbnc', logbnc, [str,int,int], float)
bnckn	= lambda row:	likelihood( int(row[1]), bnc(str(row[0])), int(row[2]), bncsum()) # assuming first 3 columns is : (word, cnt, wordsum) , row is a tuple or list
	
if __name__ == "__main__":
	pass
