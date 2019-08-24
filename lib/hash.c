/* 
   Copyright (C) 2006, 2007 Jacek Śliwerski (rzyjontko)

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

#include "xmalloc.h"
#include "hash.h"

/****************************************************************************
 *    IMPLEMENTATION PRIVATE DEFINITIONS / ENUMERATIONS / SIMPLE TYPEDEFS
 ****************************************************************************/

/**
 * This is
 *   floor (((sqrt (5) - 1) / 2) * 2 ^ 32
 */
#define KNUTH_CONST (2654435769U)

/****************************************************************************
 *    IMPLEMENTATION PRIVATE FUNCTION PROTOTYPES
 ****************************************************************************/

static unsigned hash (htable_t *table, void *s);
static entry_t *lookup_with_hash (htable_t *table, void *key, unsigned hashval);

/****************************************************************************
 *    IMPLEMENTATION PRIVATE FUNCTIONS
 ****************************************************************************/

static unsigned
hash (htable_t *table, void *s)
{
        unsigned wordval;
        int      shift = 8 * sizeof (unsigned) - table->exponent;

        wordval = table->compute_hash (s);

        return (wordval * KNUTH_CONST) >> shift;
}



static entry_t *
lookup_with_hash (htable_t *table, void *key, unsigned hashval)
{
        entry_t *entry;

        for (entry = table->array[hashval]; entry; entry = entry->next){
                if (!table->compare (entry->key, key))
                        break;
        }
        return entry;
}



static void
rehash (htable_t *table)
{
        entry_aux_t *list;
        entry_t     *item;
        unsigned     hashval;

        for (list = table->list; list; list = list->next){
                item                  = list->entry;
                hashval               = hash (table, item->key);
                item->next            = table->array[hashval];
                table->array[hashval] = item;
        }
}


static void
resize (htable_t *table)
{
        int size = 1 << table->exponent;
        if (table->count > 2 * size){
                xfree (table->array);
                table->exponent++;
                size <<= 1;
                table->array = xcalloc (size, sizeof (entry_t));
                rehash (table);
        }
}


/****************************************************************************
 *    INTERFACE FUNCTIONS
 ****************************************************************************/

htable_t *
htable_create (unsigned exponent, unsigned (*compute_hash)(void *),
               int (*compare)(void *, void *))
{
        int       size   = 1 << exponent;
        htable_t *result = xmalloc (sizeof (htable_t));

        result->exponent = exponent;
        result->count = 0;
        result->list = NULL;
        result->array = xcalloc (size, sizeof (entry_t));
        result->compute_hash = compute_hash;
        result->compare = compare;
        return result;
}


void
htable_destroy (htable_t *table, void (*fun)(void *, void *))
{
        entry_aux_t *item;

        while (table->list){
                item        = table->list;
                table->list = table->list->next;

                if (fun)
                        fun (item->entry->key, item->entry->value);
                xfree (item->entry);
                xfree (item);
        }
        xfree (table->array);
        xfree (table);
}


entry_t *
htable_lookup (htable_t *table, void *key)
{
        unsigned hashval = hash (table, key);
        return lookup_with_hash (table, key, hashval);
}




entry_t *
htable_insert (htable_t *table, void *key, void *value)
{
        unsigned     hashval = hash (table, key);
        entry_t     *found   = lookup_with_hash (table, key, hashval);
        entry_aux_t *list_item;
  
        if (found)
                return found;

        found                 = xmalloc (sizeof (entry_t));
        found->key            = key;
        found->value          = value;
        found->next           = table->array[hashval];
        table->array[hashval] = found;

        list_item        = xmalloc (sizeof (entry_aux_t));
        list_item->next  = table->list;
        list_item->entry = found;
        table->list      = list_item;

        table->count++;
        resize (table);
        return found;
}



void *
htable_fold (htable_t *table, void *(*fun)(entry_t *, void *), void *acc)
{
        entry_aux_t *list;

        for (list = table->list; list; list = list->next){
                acc = fun (list->entry, acc);
        }
        return acc;
}


unsigned
hash_str (const char *str)
{
        unsigned h = 0;
        unsigned g;

        while (*str){
                h <<= 4;
                h  += *str;
                if ((g = h & 0xf0000000)){
                        h ^= (g >> 24);
                        h ^= g;
                }
                str++;
        }
        return h;
}


/****************************************************************************
 *
 *    END MODULE hash.c
 *
 ****************************************************************************/
