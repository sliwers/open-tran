-- drop table words;
-- drop table phrases;
-- drop table canonicalphrases;
-- drop table locations;

-- drop function next_word(text);
-- drop function shorten(text,int);
-- drop function add_words();
-- drop function add_canonical(text);

create table locations (
	id		serial primary key,
	project		varchar(200) not null,
	number		int not null,
	unique(project, number)
);

create table canonicalphrases (
	id		serial primary key,
	phrase		varchar(500) not null,
	wordcount	int not null default 0,
	unique(phrase)
);

create table phrases (
	locationid 	int references locations(id) on delete cascade,
	canonicalid 	int references canonicalphrases(id) on delete cascade,
	language	char(2) not null,
	culture		char(2),
	phrase		varchar(500) not null,
	unique(locationid, canonicalid, language, culture)
);

create table words (
	canonicalid	int references canonicalphrases(id) on delete cascade,
	occurences	int not null default 0,
	word		varchar(50) not null,
	unique(canonicalid, word)
);


create function next_word(text) returns varchar(50)
as'
	DECLARE
		phrase ALIAS FOR $1;
		trstr  text;
		offset int;
		result varchar(50);
	BEGIN
		LOOP
			trstr := trim (leading from phrase);
			IF char_length(trstr) = 0 THEN
				RETURN NULL;
			END IF;
			offset := position ('' '' in trstr);
			IF offset = 0 THEN
				RETURN NULL;
			END IF;
			result := substring (trstr for offset);
			EXIT WHEN offset < 50;
		END LOOP;
		RETURN trim (trailing from result);
	END;
'
language 'plpgsql';

create function shorten(text,int) returns text
as'
	DECLARE 
		phrase ALIAS FOR $1;
		offset ALIAS FOR $2;
		new_phrase text;
	BEGIN
		new_phrase := trim (leading from phrase);
		RETURN substring(new_phrase from offset);
	END;
'
language 'plpgsql';

-- ATTENTION!
-- This trigger requires words in the phrase to be sorted!
create function add_words() returns trigger
as'
	DECLARE 
		pword	varchar(50) default null;
		nword  	varchar(50) default null;
		wordcnt	int default 0;
		phrase 	text;
		length 	int;
		cnt    	int default 0;
	BEGIN
		IF NEW.phrase IS NULL THEN
			RETURN NEW;
		END IF;
		phrase := NEW.phrase || '' '';
		LOOP
			nword := next_word(phrase);
			EXIT WHEN nword IS NULL;
			IF pword IS NOT NULL AND nword <> pword THEN
				INSERT INTO words (canonicalid, word, occurences) VALUES (NEW.id, pword, wordcnt);
				wordcnt := 1;
			ELSE
				wordcnt := wordcnt + 1;
			END IF;
			cnt    := cnt + 1;
			length := char_length(nword) + 1;
			phrase := shorten(phrase, length);
			pword  := nword;
		END LOOP;
		INSERT INTO words (canonicalid, word, occurences) VALUES (NEW.id, pword, wordcnt);
		UPDATE canonicalphrases SET wordcount = cnt WHERE id = NEW.id;
		RETURN NEW;
	END;
'
language 'plpgsql';

create trigger add_words after insert on canonicalphrases 
for each row execute procedure add_words();

create function add_canonical(text) returns int
as'
	DECLARE
		ap 	ALIAS FOR $1;
		aid	int;
	BEGIN
		SELECT INTO aid id FROM canonicalphrases WHERE phrase = ap;
		IF NOT FOUND THEN
			INSERT INTO canonicalphrases(phrase) VALUES (ap);
			SELECT INTO aid currval(''canonicalphrases_id_seq'');
		END IF;
		RETURN aid;
	END
'
language 'plpgsql'

