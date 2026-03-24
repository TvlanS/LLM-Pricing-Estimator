import sqlite3
import sqlite_vec
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.utilities import SQLDatabase
import pyprojroot
import pandas as pd
import os
import numpy as np
from openai import OpenAI
from .config_step import Config
from datetime import datetime
import json

config = Config()
now = datetime.now()

client = OpenAI(
        api_key=config.api_key,  
        base_url="https://api.deepseek.com"
    )


class TableEmbedding:
    def __init__(self, model_name = "sentence-transformers/all-MiniLM-L6-v2"):
        self.embedding_model = HuggingFaceEmbeddings(model_name = model_name)
        self.root = pyprojroot.here()
        self.excel_path = self.root/"Excel"
        self.sql_path = self.root/"SQL"

        if not os.path.exists(self.sql_path): 
            os.makedirs(self.sql_path)

    def create_database(self):
        for i in os.listdir(self.excel_path):
            if i.endswith(".csv"):
                df = pd.read_csv(self.excel_path/i)
                filename = i.split(".")[0]
                self.sql_path = f"{self.root}/SQL/{filename}.db"
                conn = sqlite3.connect(self.sql_path)
                try:
                    df.to_sql(filename, conn,index = False , if_exists = "fail")
                    print(f"Database created for {filename}")
                except:
                    print(f"Database for {filename} already exists")
                
            else :
                print(f"File {i} is not a csv file")

            cursor = conn.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                cost REAL,           
                vector BLOB
            )
            """)

            if "Job Scope" in df.columns and "Job Scope Cost" in df.columns:
                text = df["Job Scope"].tolist()
                cost = df["Job Scope Cost"].tolist()

            for txt,cost in zip(text,cost):
                vector = self.embedding_model.embed_query(txt)
                vector = np.array(vector, dtype = np.float32)
                cursor.execute("INSERT INTO embeddings (text, cost, vector) VALUES (?, ?,?)",
                (txt, cost, vector.tobytes()))
            
            conn.commit()
            conn.close()
            print(f"Embeddings stored in {filename}.db")

    @staticmethod
    def cosine_similarity(a, b):
         return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def search_embeddings(self, query, top_k=10):
    # 1. Embed the query
        query_vec = self.embedding_model.embed_query(query)
        query_vec = np.array(query_vec, dtype=np.float32)

        # 2. Connect to database
        conn = sqlite3.connect(self.sql_path)
        cursor = conn.cursor()

        # 3. Fetch all embeddings
        cursor.execute("SELECT id, text, cost, vector FROM embeddings")
        rows = cursor.fetchall()

        # 4. Compute similarity
        results = []
        for row in rows:
            row_id, text, cost ,vec_blob  = row
            vec = np.frombuffer(vec_blob, dtype=np.float32)
            sim = self.cosine_similarity(query_vec, vec)
            results.append((row_id, text, cost,sim))

        results.sort(key=lambda x: x[3], reverse=True)
        final_results = [{"Work Description": r[1], "Cost": r[2]} for r in results[:top_k]]

        conn.close()

        return final_results
    
    def search_db(self,query,k):
        output = {}
        query_split = query.split(",") 
        for i in query_split:
            results = self.search_embeddings(i,k)
            output[i] = results
            
        return output , query
    
    def create_json(self):
        filename = f"{now.strftime('%Y%m%d_%H%M%S%f')}.json"
        json_filepath = f"{self.root}/Historical/{filename}"
        print(json_filepath)
        return json_filepath
        
   
    def history(self,input , output , json_filepath):
        entry = { "Time" : now.strftime('%Y%m%d_%H%M%S%f') ,
                  "Input" : input , 
                  "Output" : output}
        try:    
            with open(json_filepath, "r", encoding ="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        data.append(entry)

        with open(json_filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    
    def LLM_output(self,query,k):
        output , query = self.search_db(query,k)

        print(output)

        response = client.chat.completions.create(
        model="deepseek-chat",  # Specify the DeepSeek model you want to use (e.g., "deepseek-chat", "deepseek-r1")
        messages=[
            {"role": "system", "content": config.prompt},
            {"role": "user", "content": "Customer Request = {customer_request} , \nHistorical Data = {historical_data}".format(customer_request = query , historical_data = output)},
        ],
        stream=False)
        print(response.choices[0].message.content)

        return response , output