#ifndef __HASH_H__
#define __HASH_H__ 1
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
 *    INTERFACE DEFINITIONS
 ****************************************************************************/

#define htable_create_s(i) \
       (htable_create ((i), (unsigned (*)(void *))hash_str, \
                       (int (*)(void *, void *))strcmp))

                

/****************************************************************************
 *    INTERFACE STRUCTURES / UTILITY CLASSES
 ****************************************************************************/

typedef struct hentry {
        struct hentry *next;
        void *key;
        void *value;
} entry_t;

typedef struct entry_aux {
        struct entry_aux *next;
        entry_t          *entry;
} entry_aux_t;

typedef struct {
        entry_t     **array;
        entry_aux_t  *list;
        unsigned      exponent;
        unsigned      count;
        unsigned    (*compute_hash)(void *);
        int         (*compare)(void *, void *);
} htable_t;

/****************************************************************************
 *    INTERFACE FUNCTION PROTOTYPES
 ****************************************************************************/

extern htable_t *htable_create (unsigned exponent, unsigned (*hash)(void *),
                                int (*compare)(void *, void *));
extern void htable_destroy (htable_t *table, void (*fun)(void *, void *));

extern entry_t *htable_lookup (htable_t *table, void *key);
extern entry_t *htable_insert (htable_t *table, void *key, void *value);

extern void *htable_fold (htable_t *table, void *(*fun)(entry_t *, void *),
                          void *acc);

extern unsigned hash_str (const char *str);

/****************************************************************************
 *
 *    END HEADER hash.h
 *
 ****************************************************************************/
#endif
