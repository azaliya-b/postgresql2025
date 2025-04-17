
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