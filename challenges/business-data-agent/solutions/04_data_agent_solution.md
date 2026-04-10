
**QUESTION:** Kolik jsme měli aktivních influencerů k 1.5.2025?

**SQL Query:**
```SQL
-- number of active influencers / users / reviewers 
WITH active_users (user_count, user_name) AS 
(
select count(DISTINCT [User]) as user_count, [User]
from [Curated].[review_dimension] rd
join [Curated].[date_dimension] dd 
on rd.Date = dd.Date
where dd.Date BETWEEN DATEADD(MONTH, -3, '2025-05-01') AND '2025-05-01' 
and rd.Score > 0.5
group by [User] having count(ReviewId)>1
)
select count(*) as active_reviewer from active_users
```