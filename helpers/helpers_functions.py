import psycopg2
from pinecone import Pinecone
from openai import OpenAI

def create_vector_embedding(client, data):
    embedding = client.embeddings.create(
        input=data,
        model="text-embedding-3-small"
    ).data[0].embedding
    return embedding

def establish_connection_db(db_config):
    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(db_config['host'], db_config['user'], db_config['dbname'], db_config['password'], db_config['sslmode'])
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    return cursor, conn

def close_connection_db(cursor, conn):
    conn.commit()
    cursor.close()
    conn.close()

def query_db(cursor, query):
    cursor.execute(query)
    return cursor.fetchall()