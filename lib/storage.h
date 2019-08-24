#ifndef __STORAGE_H__
#define __STORAGE_H__ 1
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

typedef struct storage storage_t;

typedef struct
{
        int count;
        unsigned short *project_ids;
        unsigned short *location_ids;
        int *values;
} suggestion_t;

/****************************************************************************
 *    INTERFACE DATA DECLARATIONS
 ****************************************************************************/
/****************************************************************************
 *    INTERFACE FUNCTION PROTOTYPES
 ****************************************************************************/

extern storage_t *storage_create (const char *lang);
extern void storage_destroy (storage_t *storage);

extern void storage_add (storage_t *storage, const char *text, int project_id,
                         int location_id);
extern void storage_read (storage_t *storage, const char *dbname);
extern suggestion_t *storage_suggest (storage_t *storage, const char *text);

extern int suggestion_get_count (suggestion_t *suggestion);
extern unsigned short suggestion_get_project_id (suggestion_t *suggestion, int idx);
extern unsigned short suggestion_get_location_id (suggestion_t *suggestion, int idx);
extern int suggestion_get_value (suggestion_t *suggestion, int idx);
extern void suggestion_destroy (suggestion_t *suggestion);

/****************************************************************************
 *
 *    END HEADER storage.h
 *
 ****************************************************************************/
#endif
