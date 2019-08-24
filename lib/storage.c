/* 
   Copyright (C) 2006, 2007 Jacek Śliwerski

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
*/
/****************************************************************************
 *    IMPLEMENTATION HEADERS
 ****************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <wchar.h>
#include <sqlite3.h>
#include <string.h>
#include <limits.h>

#include "xmalloc.h"
#include "hash.h"
#include "phrase.h"
#include "storage.h"

/****************************************************************************
 *    IMPLEMENTATION PRIVATE DEFINITIONS / ENUMERATIONS / SIMPLE TYPEDEFS
 ****************************************************************************/

#define DEFAULT_TOP 50

#define MIN(a, b) (((a) < (b)) ? (a) : (b))

#define SELECT_QUERY "SELECT phrase, projectid, locationid " \
                     "FROM canonical " \
                     "WHERE lang = '%s'"
#define QUERY_LEN(storage) (strlen (SELECT_QUERY) - 2 \
                            + strlen ((storage)->lang) + 1)

#define TRACE(i) (fprintf (stderr, "%d\n", i));

/****************************************************************************
 *    IMPLEMENTATION PRIVATE CLASS PROTOTYPES / EXTERNAL CLASS REFERENCES
 ****************************************************************************/
/****************************************************************************
 *    IMPLEMENTATION PRIVATE STRUCTURES / UTILITY CLASSES
 ****************************************************************************/

struct storage
{
        htable_t *words;

        int top;
        char *lang;
};

typedef struct list
{
        struct list *next;
        phrase_t *phrase;
        unsigned short location_id;
        unsigned short project_id;
        int destroy_phrase;
} list_t;


typedef struct hit
{
        int query_hits;
        int storage_hits;
} hit_t;

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
/****************************************************************************
 *    IMPLEMENTATION PRIVATE FUNCTIONS
 ****************************************************************************/

static void
add_word (htable_t *words, word_t *word, phrase_t *phrase, int project_id,
          int location_id, int destroy_phrase)
{
        entry_t *entry;
        list_t *node = xmalloc (sizeof (list_t));
        node->next = NULL;
        node->phrase = phrase;
        node->project_id = project_id;
        node->location_id = location_id;
        node->destroy_phrase = destroy_phrase;

        entry = htable_insert (words, word, node);
        if (entry->value != node){
                node->next = entry->value;
                entry->value = node;
        }
}



static unsigned
node_hash (void *key)
{
        list_t *node = (list_t *) key;
        return node->location_id;
}


static int
node_cmp (void *n1, void *n2)
{
        list_t *node1 = (list_t *) n1;
        list_t *node2 = (list_t *) n2;

        unsigned id1 = node1->project_id | (node1->location_id << 16);
        unsigned id2 = node2->project_id | (node2->location_id << 16);

        return (id1 > id2) - (id1 < id2);
}


static void
merge_and_destroy_hit (hit_t *h1, hit_t *h2)
{
        h1->query_hits += h2->query_hits;
        h1->storage_hits += h2->storage_hits;
        xfree (h2);
}


static int
compare_words (const void *p1, const void *p2)
{
        word_t **word1 = (word_t **) p1;
        word_t **word2 = (word_t **) p2;

        return phrase_compare ((phrase_t *) *word1, (phrase_t *) *word2);
}


static int
word_occurences (word_t *word, phrase_t *phrase)
{
        word_t **item = bsearch (& word, phrase->words, phrase->word_count,
                                 sizeof (word_t *), compare_words);
        return (*item)->occurences;
}


static void
hit_word (htable_t *words, htable_t *hits, word_t *word)
{
        entry_t *entry = htable_lookup (words, word);
        list_t *node = (entry) ? (list_t *) entry->value : NULL;

        while (node){
                entry_t *entry;
                hit_t *hit = xmalloc (sizeof (hit_t));
                hit->query_hits = word->occurences;
                hit->storage_hits = word_occurences (word, node->phrase);

                entry = htable_insert (hits, node, hit);
                if (entry->value != hit)
                        merge_and_destroy_hit ((hit_t *)entry->value, hit);

                node = node->next;
        }
}


static void *
extract (entry_t *entry, void *acc)
{
        entry_t **array = (entry_t **) acc;
        *array = entry;
        return array + 1;
}


static int
entries_compare (const void *p1, const void *p2)
{
        const entry_t **entry1 = (const entry_t **) p1;
        const entry_t **entry2 = (const entry_t **) p2;

        list_t *node1 = (list_t *) (*entry1)->key;
        list_t *node2 = (list_t *) (*entry2)->key;

        hit_t *hit1 = (hit_t *) (*entry1)->value;
        hit_t *hit2 = (hit_t *) (*entry2)->value;

        int val1 = node1->phrase->word_count - hit1->query_hits - hit1->storage_hits;
        int val2 = node2->phrase->word_count - hit2->query_hits - hit2->storage_hits;

        return (val1 > val2) - (val1 < val2);
}


static suggestion_t *
extract_and_sort (storage_t *storage, htable_t *hits)
{
        int i;
        entry_t **entries = alloca (hits->count * sizeof (entry_t *));
        suggestion_t *result = xmalloc (sizeof (suggestion_t));

        htable_fold (hits, extract, entries);
        qsort (entries, hits->count, sizeof (entry_t *), entries_compare);
        
        result->count = MIN (storage->top, hits->count);
        result->project_ids = xmalloc (result->count * sizeof (unsigned short));
        result->location_ids = xmalloc (result->count * sizeof (unsigned short));
        result->values = xmalloc (result->count * sizeof (int));

        for (i = 0; i < result->count; i++){
                list_t *node = (list_t *) entries[i]->key;
                hit_t *hit = (hit_t *) entries[i]->value;
                result->project_ids[i] = node->project_id;
                result->location_ids[i] = node->location_id;
                result->values[i] = node->phrase->word_count
                        - hit->query_hits - hit->storage_hits;
        }

        return result;
}


static void
destroy_hit (void *key, void *value)
{
        hit_t *hit = (hit_t *) value;
        xfree (hit);
}


static int
read_callback (void *vstorage, int argc, char **argv, char **col_names)
{
        storage_t *storage = (storage_t *) vstorage;
        storage_add (storage, argv[0], atoi (argv[1]), atoi (argv[2]));
        return 0;
}


static void
list_destroy (void *key, void *value)
{
        list_t *next;
        list_t *node = (list_t *) value;

        while (node){
                next = node->next;
                if (node->destroy_phrase){
                        phrase_destroy (node->phrase);
                }
                xfree (node);
                node = next;
        }
}


static void
destroy_storage_internals (storage_t *storage)
{
        if (storage->words)
                htable_destroy (storage->words, list_destroy);
}


static void
initialize_storage_table (storage_t *storage)
{
        storage->words =
                htable_create (16, (unsigned (*)(void *)) phrase_hash,
                               (int (*)(void *, void *)) phrase_compare);
}

/****************************************************************************
 *    INTERFACE FUNCTIONS
 ****************************************************************************/

storage_t *
storage_create (const char *lang)
{
        storage_t *result = xcalloc (1, sizeof (storage_t));

        result->top = DEFAULT_TOP;
        result->lang = xstrdup (lang);

        return result;
}


void
storage_destroy (storage_t *storage)
{
        destroy_storage_internals (storage);

        xfree (storage->lang);
        xfree (storage);
}


void
storage_add (storage_t *storage, const char *text, int project_id,
             int location_id)
{
        int i;
        phrase_t *phrase = phrase_create (text);

        if (phrase->word_count == 0){
                phrase_destroy (phrase);
                return;
        }
        
        for (i = 0; i < phrase->word_count; i++){
                add_word (storage->words, phrase->words[i], phrase,
                          project_id, location_id, i == 0);
        }
}


void
storage_read (storage_t *storage, const char *dbname)
{
        sqlite3 *db;
        int ret;
        char *errormsg;
        char *query = alloca (QUERY_LEN (storage));
        
        destroy_storage_internals (storage);
        initialize_storage_table (storage);

        ret = sqlite3_open (dbname, & db);
        if (ret){
                fprintf (stderr, "error: %s\n", sqlite3_errmsg (db));
                sqlite3_close (db);
                return;
        }

        sprintf (query, SELECT_QUERY, storage->lang);
        
        ret = sqlite3_exec (db, query, read_callback, storage,
                            & errormsg);
                            
        if (ret != SQLITE_OK){
                fprintf (stderr, "error: %s\n", sqlite3_errmsg (db));
                sqlite3_free (errormsg);
        }

        sqlite3_close (db);
}


suggestion_t *
storage_suggest (storage_t *storage, const char *text)
{
        int i;
        suggestion_t *result;

        htable_t *hits = htable_create (10, (unsigned (*)(void *)) node_hash,
                                        (int (*)(void *, void *)) node_cmp);
        phrase_t *phrase = phrase_create (text);

        for (i = 0; i < phrase->word_count; i++){
                hit_word (storage->words, hits, phrase->words[i]);
        }

        result = extract_and_sort (storage, hits);
        htable_destroy (hits, destroy_hit);
        phrase_destroy (phrase);
        return result;
}


int
suggestion_get_count (suggestion_t *suggestion)
{
        return suggestion->count;
}


unsigned short
suggestion_get_project_id (suggestion_t *suggestion, int idx)
{
        if (idx >= suggestion->count)
                return 0;

        return suggestion->project_ids[idx];
}


unsigned short
suggestion_get_location_id (suggestion_t *suggestion, int idx)
{
        if (idx >= suggestion->count)
                return 0;

        return suggestion->location_ids[idx];
}


int
suggestion_get_value (suggestion_t *suggestion, int idx)
{
        if (idx >= suggestion->count)
                return INT_MAX;

        return suggestion->values[idx];
}


void
suggestion_destroy (suggestion_t *suggestion)
{
        xfree (suggestion->project_ids);
        xfree (suggestion->location_ids);
        xfree (suggestion->values);
        xfree (suggestion);
}


/****************************************************************************
 *
 *    END MODULE storage.c
 *
 ****************************************************************************/
