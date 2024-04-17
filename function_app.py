import logging
import azure.functions as func
import psycopg2
from pinecone import Pinecone
from openai import OpenAI
from helpers import helpers_functions
import os
app = func.FunctionApp()

@app.schedule(schedule="0 0 */12 * * *", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
def cronjobembedding(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')

    DB_PASSWORD = os.getenv('DB_PASSWORD')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

    ##################### 1. The job connects to the azure postgre database and get all candidates and all jobs #####################

    cursor, conn = helpers_functions.establish_connection_db({
        'host': "candidate-finder-db.postgres.database.azure.com",
        'user': "asta_admin",
        'password': DB_PASSWORD,
        'dbname': "postgres",
        'sslmode': "require"
    })

    candidates = helpers_functions.query_db(cursor, "SELECT * FROM candidates;")
    jobs = helpers_functions.query_db(cursor, "SELECT * FROM jobs;")

    helpers_functions.close_connection_db(cursor, conn)

    logging.info('Candidates and jobs fetched from the database.')
    ##################### 2. The job then embeds these candidates and jobs into vectors with openai API #####################

    client = OpenAI(api_key=OPENAI_API_KEY)

    candidates_vectors = []
    jobs_vectors = []

    for row in candidates:
        data = (f"CV du candidat: {row[4]}")

        embedding = helpers_functions.create_vector_embedding(client, data)

        candidates_vectors.append(
            {"id": str(row[0]),
            "values": embedding,
            "metadata": {"Nom": row[1]}})

    for row in jobs:
        data = (f"Titre du poste: {row[1]}\n"
                f"Description du poste: {row[2]}\n"
                f"Nom entreprise: {row[3]}")

        embedding = helpers_functions.create_vector_embedding(client, data)

        jobs_vectors.append(
            {"id": str(row[0]),
            "values": embedding,
            "metadata": {"Titre du poste": row[1], "Nom entreprise": row[3]}})

    logging.info('Candidates and jobs vectors created.')

    ##################### 3. The job adds the candidates and jobs in their respective namespaces of the index work-matching in Pinecone #####################

    pc = Pinecone(api_key= PINECONE_API_KEY)
    index = pc.Index("candidatefinder")

    index.upsert(
        vectors=candidates_vectors,
        namespace="candidates"
    )

    index.upsert(
        vectors=jobs_vectors,
        namespace="jobs"
    )

    logging.info('Pinecone index updated with candidates and jobs vectors.')
        