/* 
   Copyright (C) 2006 Jacek Sliwerski

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; version 2.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software Foundation,
   Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.  

   ----------------------------------------------------------------------

*/
/****************************************************************************
 *    IMPLEMENTATION HEADERS
 ****************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>
#include <wctype.h>

#include "xmalloc.h"
#include "phrase.h"

/****************************************************************************
 *    IMPLEMENTATION PRIVATE DEFINITIONS / ENUMERATIONS / SIMPLE TYPEDEFS
 ****************************************************************************/

#define MIN(a, b) (((a) < (b)) ? (a) : (b))

/****************************************************************************
 *    IMPLEMENTATION PRIVATE CLASS PROTOTYPES / EXTERNAL CLASS REFERENCES
 ****************************************************************************/
/****************************************************************************
 *    IMPLEMENTATION PRIVATE STRUCTURES / UTILITY CLASSES
 ****************************************************************************/

typedef struct list
{
        struct list *next;
        word_t *word;
} list_t;


/****************************************************************************
 *    IMPLEMENTATION REQUIRED EXTERNAL REFERENCES (AVOID)
 ****************************************************************************/
/****************************************************************************
 *    IMPLEMENTATION PRIVATE DATA
 ****************************************************************************/
/****************************************************************************
 *    INTERFACE DATA
 ****************************************************************************/
/****************************************************************************
 *    IMPLEMENTATION PRIVATE FUNCTION PROTOTYPES
 ****************************************************************************/

static void word_destroy (word_t *word);

/****************************************************************************
 *    IMPLEMENTATION PRIVATE FUNCTIONS
 ****************************************************************************/

static wchar_t *
utf8_to_wchar(const unsigned char *utf, size_t *memsize)
{
        int i = 0;
        int j = 0;
	int len = strlen ((char *) utf);
	wchar_t *mem = xcalloc (len + 1, sizeof(wchar_t));

	while (i < len)
	{
		if(utf[i] < 0x80)
			mem[j++] = utf[i++];
		else if(utf[i] < 0xE0)
		{
			mem[j++] = ((utf[i] & 0x1F) << 6) |
				(utf[i + 1] & 0x3F);
			i += 2;
		}
		else if(utf[i] < 0xF0)
		{
			mem[j++] = ((utf[i] & 0x0F) << 12) |
				((utf[i + 1] & 0x3F) << 6) |
				(utf[i + 2] & 0x3F);
			i += 3;
		}
		else if(utf[i] < 0xF8)
		{
			mem[j++] = ((utf[i] & 0x07) << 18) |
				((utf[i + 1] & 0x3F) << 12) |
				((utf[i + 2] & 0x3F) << 6) |
				(utf[i + 2] & 0x3F);
			i += 4;
		}
		else if(utf[i] < 0xFC)
		{
			mem[j++] = ((utf[i] & 0x03) << 24) |
				((utf[i + 1] & 0x3F) << 18) |
				((utf[i + 2] & 0x3F) << 12) |
				((utf[i + 3] & 0x3F) << 6) |
				(utf[i + 4] & 0x3F);
			i += 5;
		}
		else if(utf[i] >= 0xFC)
		{
			mem[j++] = ((utf[i] & 0x01) << 30) |
				((utf[i + 1] & 0x3F) << 24) |
				((utf[i + 2] & 0x3F) << 18) |
				((utf[i + 3] & 0x3F) << 12) |
				((utf[i + 4] & 0x3F) << 6) |
				(utf[i + 5] & 0x3F);
			i += 6;
		}
	}

	mem = xrealloc (mem, sizeof(wchar_t) * (j + 1));
	*memsize = j;
        return mem;
}


static void
skip_nonalpha (wchar_t **text)
{
        while (**text && !iswalpha(**text))
                (*text)++;
}


static void
skip_alpha (wchar_t **text)
{
        while (**text && iswalpha(**text))
                (*text)++;
}


static int
mark_duplicates (word_t **array, int count)
{
        int i, j;
        int dups = 0;

        for (i = 0; i < count - 1; i++){
                for (j = i + 1; j < count; j++){
                        if (phrase_compare ((phrase_t *)array[i],
                                            (phrase_t *)array[j]) == 0){
                                array[i]->occurences++;
                                dups++;
                                word_destroy (array[j]);
                        } else {
                                break;
                        }
                }
                i = j - 1;
        }
        return dups;
}


static int
words_compare (const void *p1, const void *p2)
{
        const word_t **word1 = (const word_t **) p1;
        const word_t **word2 = (const word_t **) p2;

        return phrase_compare ((phrase_t *) *word1, (phrase_t *) *word2);
}


static word_t **
eliminate (list_t *list, int *count)
{
        int i, j;
        int dups;
        word_t **result;
        word_t **array = alloca (*count * sizeof (word_t *));

        for (i = 0; list; i++, list = list->next){
                array[i] = list->word;
        }

        qsort (array, *count, sizeof (word_t *), words_compare);
        dups = mark_duplicates (array, *count);
        *count -= dups;
        result = xmalloc (*count * sizeof (word_t *));

        for (i = 0, j = 0; j < *count + dups; i++){
                result[i] = array[j];
                j += array[j]->occurences;
        }

        return result;
}


static word_t *
word_create (wchar_t *text, int length)
{
        int i;
        word_t *result = xmalloc (sizeof (word_t));
        result->text = text;
        result->length = length;
        result->occurences = 1;

        for (i = 0; i < length; i++)
                result->text[i] = towlower (result->text[i]);

        return result;
}


static void
word_destroy (word_t *word)
{
        xfree (word);
}


/****************************************************************************
 *    INTERFACE FUNCTIONS
 ****************************************************************************/


unsigned
phrase_hash (phrase_t *phrase)
{
        int i;
        unsigned h = 0;
        unsigned g;

        for (i = 0; i < phrase->length; i++){
                h <<= 4;
                h  += phrase->text[i];
                if ((g = h & 0xf0000000)){
                        h ^= (g >> 24);
                        h ^= g;
                }
        }
        return h;
}


int
phrase_compare (phrase_t *phrase1, phrase_t *phrase2)
{
        int len1 = phrase1->length;
        int len2 = phrase2->length;

        int ret = wcsncasecmp (phrase1->text, phrase2->text, MIN (len1, len2));

        if (ret != 0)
                return -ret;

        return (len1 < len2) - (len1 > len2);
}


void
phrase_print (phrase_t *phrase)
{
        int i;

        for (i = 0; i < phrase->length; i++){
                printf ("%lc", phrase->text[i]);
        }
}


phrase_t *
phrase_create (const char *text)
{
        int count = 0;
        size_t length;
        wchar_t *ptr;
        wchar_t *word;
        list_t *list = NULL;
        phrase_t *result = xmalloc (sizeof (phrase_t));

        result->text = utf8_to_wchar ((const unsigned char *) text, & length);
        result->length = length;

        ptr = result->text;

        do {
                skip_nonalpha (& ptr);
                word = ptr;
                skip_alpha (& ptr);
                if (*word){
                        list_t *node = alloca (sizeof (list_t));
                        node->word = word_create (word, ptr - word);
                        node->next = list;
                        list = node;
                        count++;
                }
        } while (*ptr);

        result->words = eliminate (list, & count);
        result->word_count = count;
        
        return result;
}


void
phrase_destroy (phrase_t *phrase)
{
        int i;

        for (i = 0; i < phrase->word_count; i++)
                word_destroy (phrase->words[i]);

        xfree (phrase->text);
        if (phrase->words)
                xfree (phrase->words);
        xfree (phrase);
}

/****************************************************************************
 *
 *    END MODULE phrase.c
 *
 ****************************************************************************/
