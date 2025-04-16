-- Q1: Репутационные пары
WITH PostgresqlQuestions AS (
    SELECT Id, CreationDate, Tags
    FROM Posts
    WHERE PostTypeId = 1 AND Tags LIKE '%|postgresql|%'
),
Answers AS (
    SELECT p.Id AS AnswerId, p.ParentId, p.CreationDate AS AnswerDate, p.OwnerUserId, u.Reputation
    FROM Posts p
    JOIN Users u ON u.Id = p.OwnerUserId
    WHERE p.PostTypeId = 2
),
QnA AS (
    SELECT q.Id AS QuestionId,
           q.CreationDate AS QuestionDate,
           a.AnswerDate,
           a.Reputation,
           q.Tags
    FROM PostgresqlQuestions q
    JOIN Answers a ON a.ParentId = q.Id
),
TagPairs AS (
    SELECT
        t1.tag AS tag1,
        t2.tag AS tag2,
        EXTRACT(EPOCH FROM (qna.AnswerDate - qna.QuestionDate)) / 3600 AS hours_to_answer,
        qna.Reputation
    FROM QnA qna
    CROSS JOIN LATERAL unnest(string_to_array(trim(BOTH '|' FROM qna.Tags), '|')) AS t1(tag)
    CROSS JOIN LATERAL unnest(string_to_array(trim(BOTH '|' FROM qna.Tags), '|')) AS t2(tag)
    WHERE t1.tag < t2.tag
)
SELECT
    tag1,
    tag2,
    COUNT(*) AS pair_count,
    ROUND(AVG(hours_to_answer), 2) AS avg_hours_to_answer,
    ROUND(AVG(Reputation)) AS avg_user_reputation
FROM TagPairs
GROUP BY tag1, tag2
HAVING COUNT(*) > 3
ORDER BY pair_count DESC
LIMIT 20;

-- Q2: Успешные шутники
WITH Questions AS (
    SELECT
        Id AS question_id,
        AcceptedAnswerId,
        Tags
    FROM Posts
    WHERE PostTypeId = 1 AND Tags LIKE '%postgresql%'
),
AcceptedBadAnswers AS (
    SELECT
        p.Id AS answer_id,
        p.Score,
        u.DisplayName,
        q.question_id
    FROM Questions q
    JOIN Posts p ON p.Id = q.AcceptedAnswerId AND p.Score < 0
    LEFT JOIN Users u ON u.Id = p.OwnerUserId
)
SELECT *
FROM AcceptedBadAnswers
ORDER BY Score ASC;