# 2025.10.13
import os,fire # fire>=0.7.1  wget>=3.2
host	= 'file.yulk.net'
root	= os.path.dirname(os.path.abspath(__file__)) #D:\cikuu\mod\yulk

def download_with_wget(url, local_filename):
	import wget
	try:
		if os.path.exists(local_filename):
			os.remove(local_filename)
		print ("Start to download: ",  url , flush=True) 
		wget.download(url, local_filename)
		print(f"\nDone: {local_filename}")
	except Exception as e:
		print(f"\nFailed: {e}", url, local_filename)

# python __main__.py par lemword
par		= lambda name : download_with_wget(f"http://{host}/par/{name}.parquet", root +f"/par/{name}.parquet")
park	= lambda name : download_with_wget(f"http://{host}/park/{name}.parquet", root +f"/park/{name}.parquet")
parkv	= lambda name : download_with_wget(f"http://{host}/parkv/{name}.parquet", root +f"/parkv/{name}.parquet")
en		= lambda name : download_with_wget(f"http://{host}/en/{name}.parquet", root +f"/en/{name}.parquet")
cn		= lambda name : download_with_wget(f"http://{host}/cn/{name}.parquet", root +f"/cn/{name}.parquet")

if __name__ == "__main__": 	
	fire.Fire()
