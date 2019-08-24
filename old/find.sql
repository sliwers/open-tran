select dc.id, dc.phrase, min(sp.note) as note, count(*) as cnt
from
(
	select sp.locationid, sp.phrase,
--		(sc.wordcount - sw.occ) / cast (sc.wordcount as float) as anote,
--		(2 - sw.cnt) / 2.0 as bnote,
		sc.wordcount - sw.occ - sw.cnt as note
	from
	(
		select canonicalid, count(*) as cnt, sum(occurences) as occ
		from words
		where word in ('save', 'as')
		group by canonicalid
	) as sw join canonicalphrases sc on sw.canonicalid = sc.id join phrases sp on sp.canonicalid = sc.id
	where sp.language = 'C'
) as sp join phrases dp on sp.locationid = dp.locationid
	join canonicalphrases dc on dc.id = dp.canonicalid
where dp.language = 'pl'
group by dc.id, dc.phrase
order by note asc, cnt desc
limit 10
