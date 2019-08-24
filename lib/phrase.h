#ifndef __PHRASE_H__
#define __PHRASE_H__ 1
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

*/
/****************************************************************************
 *    INTERFACE REQUIRED HEADERS
 ****************************************************************************/
/****************************************************************************
 *    INTERFACE DEFINITIONS
 ****************************************************************************/

#define htable_create_p(i) \
       (htable_create ((i), (unsigned (*)(void *))phrase_hash, \
                       (int (*)(void *, void *))phrase_compare))

/****************************************************************************
 *    INTERFACE STRUCTURES
 ****************************************************************************/

typedef struct
{
        wchar_t *text;
        int length;

        int occurences;
} word_t;


typedef struct
{
        wchar_t *text;
        int length;

        int word_count;
        word_t **words;
} phrase_t;

/****************************************************************************
 *    INTERFACE FUNCTION PROTOTYPES
 ****************************************************************************/

extern phrase_t *phrase_create (const char *text);
extern void phrase_destroy (phrase_t *phrase);

extern unsigned phrase_hash (phrase_t *phrase);
extern int phrase_compare (phrase_t *phrase1, phrase_t *phrase2);
extern void phrase_print (phrase_t *phrase);

/****************************************************************************
 *
 *    END HEADER phrase.h
 *
 ****************************************************************************/
#endif
