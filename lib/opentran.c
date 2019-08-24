/* 
   open-tran.eu

   Copyright (C) 2008 Jacek Śliwerski

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

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sqlite3.h>

#include "opentran.h"
#include "xmalloc.h"
#include "hash.h"
#include "phrase.h"

/****************************************************************************
 *    IMPLEMENTATION PRIVATE DEFINITIONS / ENUMERATIONS / SIMPLE TYPEDEFS
 ****************************************************************************/
/****************************************************************************
 *    IMPLEMENTATION PRIVATE CLASS PROTOTYPES / EXTERNAL CLASS REFERENCES
 ****************************************************************************/
/****************************************************************************
 *    IMPLEMENTATION PRIVATE STRUCTURES / UTILITY CLASSES
 ****************************************************************************/

struct lang_db
{
        char *lang;
        sqlite3 *db;
};

struct ot_db
{
        char *path;
        struct lang_db src;
        struct lang_db dst;
};

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

static char *
full_path (const char *path, const char *lang)
{
        int len = strlen (path) + strlen ("/nine-") + strlen (lang)
                + strlen (".db");
        char *result = xmalloc (len + 1);

        sprintf ("%s/nine-%s.db", path, lang);
        return result;
}


static sqlite3 *
open_sqlite_db (const char *path, const char *lang)
{
        int ret;
        sqlite3 *result;
        char *fpath = full_path (path, lang);

        ret = sqlite3_open (fpath, & result);
        if (ret){
                fprintf (stderr, "error: %s\n", sqlite3_errmsg (result));
                sqlite3_close (result);
                result = NULL;
        }
        
        xfree (fpath);
        return result;
}


static int
open_db (const char *path, struct lang_db *db, const char *lang)
{
        if (db->lang && !strcmp (lang, db->lang) && db->db)
                return 0;

        if (db->db)
                sqlite3_close (db->db);

        if (db->lang){
                xfree (db->lang);
                db->lang = NULL;
        }

        db->db = open_sqlite_db (path, lang);
        if (db->db)
                db->lang = xstrdup (lang);

        return db->db == NULL;
}


/****************************************************************************
 *    INTERFACE FUNCTIONS
 ****************************************************************************/


ot_db_t *
ot_open_db (const char *path)
{
        ot_db_t *result;

        result = xmalloc (sizeof (ot_db_t));
        result->path = xstrdup (path);
        result->src.lang = NULL;
        result->dst.lang = NULL;
        result->src.db = NULL;
        result->dst.db = NULL;

        return result;
}


ot_suggestion_t **
ot_suggest2 (ot_db_t *db, const char *phrase, const char *srclang,
             const char *dstlang)
{
        if (open_db (db->path, &(db->src), srclang) || open_db (db->path, &(db->dst), dstlang))
                return NULL;

        
        
        return NULL;
}


inline ot_suggestion_t **
ot_suggest (ot_db_t *db, const char *phrase, const char *dstlang)
{
        return ot_suggest2 (db, phrase, "en", dstlang);
}


void
ot_close_db (ot_db_t *db)
{
        if (db->src.db){
                sqlite3_close (db->src.db);
                db->src.db = NULL;
        }

        if (db->dst.db){
                sqlite3_close (db->dst.db);
                db->dst.db = NULL;
        }

        if (db->src.lang){
                xfree (db->src.lang);
                db->src.lang = NULL;
        }

        if (db->dst.lang){
                xfree (db->dst.lang);
                db->dst.lang = NULL;
        }

        xfree (db->path);
        xfree (db);
}


/****************************************************************************
 *    INTERFACE CLASS BODIES
 ****************************************************************************/
/****************************************************************************
 *
 *    END MODULE opentran.c
 *
 ****************************************************************************/
