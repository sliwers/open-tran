#ifndef __OPENTRAN_H__
#define __OPENTRAN_H__ 1
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

*/
/****************************************************************************
 *    INTERFACE REQUIRED HEADERS
 ****************************************************************************/
/****************************************************************************
 *    INTERFACE DEFINITIONS / ENUMERATIONS / SIMPLE TYPEDEFS
 ****************************************************************************/
/****************************************************************************
 *    INTERFACE CLASS PROTOTYPES / EXTERNAL CLASS REFERENCES
 ****************************************************************************/
/****************************************************************************
 *    INTERFACE STRUCTURES / UTILITY CLASSES
 ****************************************************************************/

typedef struct ot_db ot_db_t;

typedef struct
{
        const char *name;
        char *orig_phrase;
        int count;
} ot_project_t;

typedef struct
{
        short value;
        char *text;
        int count;
} ot_suggestion_t;

/****************************************************************************
 *    INTERFACE DATA DECLARATIONS
 ****************************************************************************/
/****************************************************************************
 *    INTERFACE FUNCTION PROTOTYPES
 ****************************************************************************/

extern ot_db_t *ot_open_db (const char *path);
extern ot_suggestion_t **ot_suggest2 (ot_db_t *db, const char *phrase,
                                      const char *srclang, const char *dstlang);
extern ot_suggestion_t **ot_suggest (ot_db_t *db, const char *phrase,
                                     const char *dstlang);
extern void ot_close_db (ot_db_t *db);

/****************************************************************************
 *    INTERFACE OBJECT CLASS DEFINITIONS
 ****************************************************************************/
/****************************************************************************
 *    INTERFACE TRAILING HEADERS
 ****************************************************************************/
/****************************************************************************
 *
 *    END HEADER opentran.h
 *
 ****************************************************************************/
#endif
