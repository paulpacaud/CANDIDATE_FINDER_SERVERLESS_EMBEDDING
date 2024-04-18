# CANDIDATE_FINDER_SERVERLESS_EMBEDDING

Ce repository contient le code de la fonction serverless synchronisant périodiquement la base de données PostgreSQl à la base de données vectorielle. Elle comporte trois étapes:
1. The job connects to the azure postgre database and get all candidates and all jobs
2. The job then embeds these candidates and jobs into vectors with openai API
3. The job adds the candidates and jobs in their respective namespaces of the index work-matching in Pinecone

La fonction est écrite en python, testée avec pytest, et déployée sur Azure Function App en serverless.
