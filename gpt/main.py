from llama_index import download_loader, GPTVectorStoreIndex

GoogleDriveReader = download_loader("GoogleDriveReader")

loader = GoogleDriveReader()

documents = loader.load_data(file_ids=['10jTjpt-uV2CWGVg57FkimwfzT1XLJHU8'])
index = GPTVectorStoreIndex(documents)
query_engine = index.as_query_engine()

while True:
    prompt = input("Type prompt...")
    response = query_engine.query(prompt)
    print(response)
