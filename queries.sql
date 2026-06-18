
-- Frequency per position: for each ball position (including power_ball), shows how many times
-- each number appeared and what % of all drawings that represents.
WITH total AS (SELECT COUNT(*) AS total_draws FROM drawings)
SELECT
    col,
    ball_number,
    appearances,
    ROUND(appearances * 100.0 / total_draws, 2) AS pct_of_draws
FROM (
    SELECT 'first_ball'  AS col, first_ball  AS ball_number, COUNT(*) AS appearances FROM drawings GROUP BY first_ball
    UNION ALL
    SELECT 'second_ball' AS col, second_ball AS ball_number, COUNT(*) AS appearances FROM drawings GROUP BY second_ball
    UNION ALL
    SELECT 'third_ball'  AS col, third_ball  AS ball_number, COUNT(*) AS appearances FROM drawings GROUP BY third_ball
    UNION ALL
    SELECT 'fourth_ball' AS col, fourth_ball AS ball_number, COUNT(*) AS appearances FROM drawings GROUP BY fourth_ball
    UNION ALL
    SELECT 'fifth_ball'  AS col, fifth_ball  AS ball_number, COUNT(*) AS appearances FROM drawings GROUP BY fifth_ball
    UNION ALL
    SELECT 'power_ball'  AS col, power_ball  AS ball_number, COUNT(*) AS appearances FROM drawings GROUP BY power_ball
) counts
CROSS JOIN total
ORDER BY
    CASE col
        WHEN 'first_ball'  THEN 1
        WHEN 'second_ball' THEN 2
        WHEN 'third_ball'  THEN 3
        WHEN 'fourth_ball' THEN 4
        WHEN 'fifth_ball'  THEN 5
        WHEN 'power_ball'  THEN 6
    END,
    ball_number;

-- Sequential pair transitions (first_ball -> second_ball): for each value that appeared in
-- first_ball, shows every value it was paired with in second_ball and how often (as a % of
-- that first_ball number's total appearances). Reveals which numbers tend to follow each other.
WITH pair_counts AS (
    SELECT
        first_ball  AS from_num,
        second_ball AS to_num,
        COUNT(*) AS pair_count
    FROM drawings
    GROUP BY first_ball, second_ball
),
from_totals AS (
    SELECT first_ball AS from_num, COUNT(*) AS from_count
    FROM drawings
    GROUP BY first_ball
)
SELECT
    'first_ball -> second_ball' AS transition,
    p.from_num,
    p.to_num,
    p.pair_count,
    ROUND(p.pair_count * 100.0 / f.from_count, 2) AS pct_of_from_appearances
FROM pair_counts p
JOIN from_totals f ON p.from_num = f.from_num
ORDER BY p.from_num, pair_count DESC;

-- Pair: second_ball -> third_ball
WITH pair_counts AS (
    SELECT
        second_ball AS from_num,
        third_ball  AS to_num,
        COUNT(*) AS pair_count
    FROM drawings
    GROUP BY second_ball, third_ball
),
from_totals AS (
    SELECT second_ball AS from_num, COUNT(*) AS from_count
    FROM drawings
    GROUP BY second_ball
)
SELECT
    'second_ball -> third_ball' AS transition,
    p.from_num,
    p.to_num,
    p.pair_count,
    ROUND(p.pair_count * 100.0 / f.from_count, 2) AS pct_of_from_appearances
FROM pair_counts p
JOIN from_totals f ON p.from_num = f.from_num
ORDER BY p.from_num, pct_of_from_appearances DESC;

-- Pair: third_ball -> fourth_ball
WITH pair_counts AS (
    SELECT
        third_ball  AS from_num,
        fourth_ball AS to_num,
        COUNT(*) AS pair_count
    FROM drawings
    GROUP BY third_ball, fourth_ball
),
from_totals AS (
    SELECT third_ball AS from_num, COUNT(*) AS from_count
    FROM drawings
    GROUP BY third_ball
)
SELECT
    'third_ball -> fourth_ball' AS transition,
    p.from_num,
    p.to_num,
    p.pair_count,
    ROUND(p.pair_count * 100.0 / f.from_count, 2) AS pct_of_from_appearances
FROM pair_counts p
JOIN from_totals f ON p.from_num = f.from_num
ORDER BY p.from_num, pct_of_from_appearances DESC;

-- Pair: fourth_ball -> fifth_ball
WITH pair_counts AS (
    SELECT
        fourth_ball AS from_num,
        fifth_ball  AS to_num,
        COUNT(*) AS pair_count
    FROM drawings
    GROUP BY fourth_ball, fifth_ball
),
from_totals AS (
    SELECT fourth_ball AS from_num, COUNT(*) AS from_count
    FROM drawings
    GROUP BY fourth_ball
)
SELECT
    'fourth_ball -> fifth_ball' AS transition,
    p.from_num,
    p.to_num,
    p.pair_count,
    ROUND(p.pair_count * 100.0 / f.from_count, 2) AS pct_of_from_appearances
FROM pair_counts p
JOIN from_totals f ON p.from_num = f.from_num
ORDER BY p.from_num, pct_of_from_appearances DESC;



-- White ball frequency on winning tickets: how often each white ball number appeared
-- across all five positions in drawings where winner = TRUE, as a % of total winning draws.
WITH winning_draws AS (
    SELECT * FROM drawings WHERE winner = TRUE
),
total_winning AS (
    SELECT COUNT(*) AS total_wins FROM winning_draws
)
SELECT
    ball_number,
    SUM(appearances) AS total_appearances_on_winning_draws,
    ROUND(SUM(appearances) * 100.0 / total_wins, 2) AS pct_of_winning_draws
FROM (
    SELECT first_ball  AS ball_number, COUNT(*) AS appearances FROM winning_draws GROUP BY first_ball
    UNION ALL
    SELECT second_ball AS ball_number, COUNT(*) AS appearances FROM winning_draws GROUP BY second_ball
    UNION ALL
    SELECT third_ball  AS ball_number, COUNT(*) AS appearances FROM winning_draws GROUP BY third_ball
    UNION ALL
    SELECT fourth_ball AS ball_number, COUNT(*) AS appearances FROM winning_draws GROUP BY fourth_ball
    UNION ALL
    SELECT fifth_ball  AS ball_number, COUNT(*) AS appearances FROM winning_draws GROUP BY fifth_ball
) counts
CROSS JOIN total_winning
GROUP BY ball_number, total_wins
ORDER BY ball_number DESC;




-- Power ball frequency on winning tickets: same as above but for the power ball only,
-- ordered by most frequent on winning draws.
WITH winning_draws AS (
    SELECT * FROM drawings WHERE winner = TRUE
),
total_winning AS (SELECT COUNT(*) AS total_wins FROM winning_draws)
SELECT
    power_ball AS ball_number,
    COUNT(*) AS appearances,
    ROUND(COUNT(*) * 100.0 / total_wins, 2) AS pct_of_winning_draws,
    'power_ball' AS ball_type
FROM winning_draws
CROSS JOIN total_winning
GROUP BY power_ball, total_wins
ORDER BY pct_of_winning_draws DESC;



-- White ball frequency by winning state: breaks down which white ball numbers appeared most
-- on winning tickets for each state, as a % of that state's total wins.
WITH state_draws AS (
    SELECT winner_state, COUNT(*) AS state_win_count
    FROM drawings
    WHERE winner = TRUE AND winner_state IS NOT NULL
    GROUP BY winner_state
),
state_ball_counts AS (
    SELECT winner_state, ball_number, COUNT(*) AS appearances
    FROM (
        SELECT winner_state, first_ball  AS ball_number FROM drawings WHERE winner = TRUE AND winner_state IS NOT NULL
        UNION ALL
        SELECT winner_state, second_ball AS ball_number FROM drawings WHERE winner = TRUE AND winner_state IS NOT NULL
        UNION ALL
        SELECT winner_state, third_ball  AS ball_number FROM drawings WHERE winner = TRUE AND winner_state IS NOT NULL
        UNION ALL
        SELECT winner_state, fourth_ball AS ball_number FROM drawings WHERE winner = TRUE AND winner_state IS NOT NULL
        UNION ALL
        SELECT winner_state, fifth_ball  AS ball_number FROM drawings WHERE winner = TRUE AND winner_state IS NOT NULL
    ) unpivoted
    GROUP BY winner_state, ball_number
)
SELECT
    s.winner_state,
    s.state_win_count AS wins_from_state,
    b.ball_number,
    b.appearances,
    ROUND(b.appearances * 100.0 / s.state_win_count, 2) AS pct_of_state_wins
FROM state_ball_counts b
JOIN state_draws s ON b.winner_state = s.winner_state
ORDER BY s.winner_state, pct_of_state_wins DESC;



-- Power ball frequency by winning state: same as above but for the power ball only.
WITH state_draws AS (
    SELECT winner_state, COUNT(*) AS state_win_count
    FROM drawings
    WHERE winner = TRUE AND winner_state IS NOT NULL
    GROUP BY winner_state
)
SELECT
    d.winner_state,
    s.state_win_count AS wins_from_state,
    d.power_ball AS ball_number,
    COUNT(*) AS appearances,
    ROUND(COUNT(*) * 100.0 / s.state_win_count, 2) AS pct_of_state_wins,
    'power_ball' AS ball_type
FROM drawings d
JOIN state_draws s ON d.winner_state = s.winner_state
WHERE d.winner = TRUE AND d.winner_state IS NOT NULL
GROUP BY d.winner_state, d.power_ball, s.state_win_count
ORDER BY d.winner_state, pct_of_state_wins DESC;




-- Overall white ball frequency (position-agnostic): collapses all five white ball positions
-- into one pool to show each number's total appearances and % across all draws, regardless
-- of which position it was drawn in.
WITH total AS (SELECT COUNT(*) AS total_draws FROM drawings)
SELECT
    ball_number,
    COUNT(*) AS total_appearances,
    ROUND(COUNT(*) * 100.0 / total_draws, 2) AS pct_of_draws
FROM (
    SELECT first_ball  AS ball_number FROM drawings
    UNION ALL
    SELECT second_ball AS ball_number FROM drawings
    UNION ALL
    SELECT third_ball  AS ball_number FROM drawings
    UNION ALL
    SELECT fourth_ball AS ball_number FROM drawings
    UNION ALL
    SELECT fifth_ball  AS ball_number FROM drawings
) all_balls
CROSS JOIN total
GROUP BY ball_number, total_draws
ORDER BY pct_of_draws DESC;




-- Win rate by day of week: total draws and wins per drawing day (Mon=0, Wed=2, Sat=5)
-- with win % to see if any day correlates with more jackpot hits.
SELECT
    day_of_week,
    COUNT(*) AS total_draws,
    SUM(CASE WHEN winner = TRUE THEN 1 ELSE 0 END) AS total_wins,
    ROUND(
        SUM(CASE WHEN winner = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        2
    ) AS win_pct
FROM drawings
GROUP BY day_of_week
ORDER BY
    CASE day_of_week
        WHEN 0    THEN 1
        WHEN 2 THEN 2
        WHEN 5  THEN 3
    END;


-- Win rate by month: same breakdown by calendar month to surface any seasonal patterns.
SELECT
    EXTRACT(MONTH FROM date_drawn)::INT AS month_num,
    TO_CHAR(date_drawn, 'Month') AS month_name,
    COUNT(*) AS total_draws,
    SUM(CASE WHEN winner = TRUE THEN 1 ELSE 0 END) AS total_wins,
    ROUND(
        SUM(CASE WHEN winner = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        2
    ) AS win_pct
FROM drawings
GROUP BY month_num, month_name
ORDER BY month_num;



-- Win rate by year: same breakdown annually to show how jackpot frequency has changed over time.
SELECT
    EXTRACT(YEAR FROM date_drawn)::INT AS year,
    COUNT(*) AS total_draws,
    SUM(CASE WHEN winner = TRUE THEN 1 ELSE 0 END) AS total_wins,
    ROUND(
        SUM(CASE WHEN winner = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        2
    ) AS win_pct
FROM drawings
GROUP BY year
ORDER BY year;


-- Days since last win (per winning draw): for each winning drawing, shows the previous
-- winning date and how many days elapsed between them — the raw streak data.
WITH wins AS (
    SELECT
        date_drawn,
        winner_state,
        LAG(date_drawn) OVER (ORDER BY date_drawn) AS prev_win_date
    FROM drawings
    WHERE winner = TRUE
)
SELECT
    date_drawn AS win_date,
    prev_win_date,
    winner_state,
    (date_drawn - prev_win_date) AS days_since_last_win
FROM wins
ORDER BY date_drawn;




-- Win streak summary stats: min, max, average, and median number of days between
-- consecutive jackpot wins across all history.
WITH wins AS (
    SELECT
        date_drawn,
        LAG(date_drawn) OVER (ORDER BY date_drawn) AS prev_win_date
    FROM drawings
    WHERE winner = TRUE
),
gaps AS (
    SELECT (date_drawn - prev_win_date) AS gap_days
    FROM wins
    WHERE prev_win_date IS NOT NULL
)
SELECT
    MIN(gap_days)                                     AS shortest_streak_days,
    MAX(gap_days)                                     AS longest_streak_days,
    AVG(gap_days)                                    AS avg_days_between_wins,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY gap_days) AS median_days_between_wins
FROM gaps;



-- Win gap distribution: buckets the time between consecutive wins into ranges (1 week,
-- 2 weeks, 1 month, etc.) with counts and % to show how streaks are distributed.
WITH wins AS (
    SELECT
        date_drawn,
        LAG(date_drawn) OVER (ORDER BY date_drawn) AS prev_win_date
    FROM drawings
    WHERE winner = TRUE
),
gaps AS (
    SELECT
        (date_drawn - prev_win_date) AS gap_interval,
        EXTRACT(EPOCH FROM (date_drawn - prev_win_date)) / 86400 AS gap_days
    FROM wins
    WHERE prev_win_date IS NOT NULL
)
SELECT
    CASE
        WHEN gap_days <= 7   THEN '01. 1-7 days (back to back weeks)'
        WHEN gap_days <= 14  THEN '02. 8-14 days (2 weeks)'
        WHEN gap_days <= 30  THEN '03. 15-30 days (1 month)'
        WHEN gap_days <= 60  THEN '04. 31-60 days (2 months)'
        WHEN gap_days <= 90  THEN '05. 61-90 days (3 months)'
        WHEN gap_days <= 180 THEN '06. 91-180 days (6 months)'
        WHEN gap_days <= 365 THEN '07. 181-365 days (1 year)'
        ELSE                      '08. 365+ days (over a year)'
    END AS gap_bucket,
    COUNT(*) AS occurrences,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct_of_all_gaps
FROM gaps
GROUP BY gap_bucket
ORDER BY gap_bucket;




