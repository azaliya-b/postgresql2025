from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()  # Загружаем переменные окружения из .env

conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT")
)

def execute_cleanup(sql):
    print("Executing:", sql.strip().split('\n')[0] + " ...")
    cur.execute(sql)
    conn.commit()

cleanup_queries = [
    # Posts
    "UPDATE Posts SET OwnerUserId = NULL WHERE OwnerUserId IS NOT NULL AND OwnerUserId NOT IN (SELECT Id FROM Users);",
    "UPDATE Posts SET LastEditorUserId = NULL WHERE LastEditorUserId IS NOT NULL AND LastEditorUserId NOT IN (SELECT Id FROM Users);",
    "UPDATE Posts SET ParentId = NULL WHERE ParentId IS NOT NULL AND ParentId NOT IN (SELECT Id FROM Posts);",
    "UPDATE Posts SET AcceptedAnswerId = NULL WHERE AcceptedAnswerId IS NOT NULL AND AcceptedAnswerId NOT IN (SELECT Id FROM Posts);",

    # Tags
    "UPDATE Tags SET ExcerptPostId = NULL WHERE ExcerptPostId IS NOT NULL AND ExcerptPostId NOT IN (SELECT Id FROM Posts);",
    "UPDATE Tags SET WikiPostId = NULL WHERE WikiPostId IS NOT NULL AND WikiPostId NOT IN (SELECT Id FROM Posts);",

    # Votes
    "DELETE FROM Votes WHERE PostId IS NOT NULL AND PostId NOT IN (SELECT Id FROM Posts);",

    # Badges
    "DELETE FROM Badges WHERE UserId IS NOT NULL AND UserId NOT IN (SELECT Id FROM Users);",

    # PostHistory
    "DELETE FROM PostHistory WHERE PostId IS NOT NULL AND PostId NOT IN (SELECT Id FROM Posts);",
    "DELETE FROM PostHistory WHERE UserId IS NOT NULL AND UserId NOT IN (SELECT Id FROM Users);",

    # PostLinks
    "DELETE FROM PostLinks WHERE PostId IS NOT NULL AND PostId NOT IN (SELECT Id FROM Posts);",
    "DELETE FROM PostLinks WHERE RelatedPostId IS NOT NULL AND RelatedPostId NOT IN (SELECT Id FROM Posts);",

    # Comments
    "DELETE FROM Comments WHERE PostId IS NOT NULL AND PostId NOT IN (SELECT Id FROM Posts);",
    "DELETE FROM Comments WHERE UserId IS NOT NULL AND UserId NOT IN (SELECT Id FROM Users);"
]

if __name__ == "__main__":
    for query in cleanup_queries:
        execute_cleanup(query)

    print("🧼 Очистка завершена.")
    cur.close()
    conn.close()
