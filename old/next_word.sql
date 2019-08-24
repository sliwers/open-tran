drop trigger add_words on canonicalphrases;
drop function next_word(text);
drop function shorten(text,int);
drop function add_words();

create function next_word(text) returns varchar(50)
as'
	DECLARE
		phrase ALIAS FOR $1;
		trstr  text;
		offset int;
		result varchar(50);
	BEGIN
		trstr := trim (leading from phrase);
		IF char_length(trstr) = 0 THEN
			RETURN NULL;
		END IF;
		offset := position ('' '' in trstr);
		IF offset = 0 THEN
			RETURN NULL;
		END IF;
		result := substring (trstr for offset);
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

create function add_words() returns trigger
as'
	DECLARE 
		nword  varchar(50);
		phrase text;
		length int;
		cnt    int default 0;
	BEGIN
		IF NEW.phrase IS NULL THEN
			RETURN NEW;
		END IF;
		phrase := NEW.phrase || '' '';
		LOOP
			nword  := next_word(phrase);
			EXIT WHEN nword IS NULL;
			INSERT INTO words (canonicalid, word) VALUES (NEW.id, nword);
			cnt    := cnt + 1;
			length := char_length(nword) + 1;
			phrase := shorten(phrase, length);
		END LOOP;
		UPDATE canonicalphrases SET wordcount = cnt WHERE id = NEW.id;
		RETURN NEW;
	END;
'
language 'plpgsql';

create trigger add_words after insert on canonicalphrases 
for each row execute procedure add_words();
