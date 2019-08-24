%module tran
%{
/*
  Copyright (C) 2007 Jacek Śliwerski (rzyjontko)

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
#include "storage.h"
%}

storage_t *storage_create (const char *lang);
void storage_destroy (storage_t *storage);

void storage_add (storage_t *storage, const char *text, int project_id,
                  int location_id);
void storage_read (storage_t *storage, const char *dbname);
suggestion_t *storage_suggest (storage_t *storage, const char *text);

int suggestion_get_count (suggestion_t *suggestion);
unsigned short suggestion_get_project_id (suggestion_t *suggestion, int idx);
unsigned short suggestion_get_location_id (suggestion_t *suggestion, int idx);
int suggestion_get_value (suggestion_t *suggestion, int idx);
void suggestion_destroy (suggestion_t *suggestion);
