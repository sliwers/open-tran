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

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <error.h>

#ifdef XMALLOC_DEBUG
# include <execinfo.h>
# include <malloc.h>
#endif


/****************************************************************************
 *    IMPLEMENTATION PRIVATE DEFINITIONS / ENUMERATIONS / SIMPLE TYPEDEFS
 ****************************************************************************/

#ifndef XMALLOC_DEPTH
# define XMALLOC_DEPTH 1
#endif

/****************************************************************************
 *    IMPLEMENTATION PRIVATE DATA
 ****************************************************************************/

#ifdef XMALLOC_DEBUG

static FILE *fp = NULL;

#endif

/****************************************************************************
 *    IMPLEMENTATION PRIVATE FUNCTION PROTOTYPES
 ****************************************************************************/

#ifdef XMALLOC_DEBUG

static void my_init_hook (void);

/* Override initializing hook from the C library. */
void (*__malloc_initialize_hook) (void) = my_init_hook;

#endif

/****************************************************************************
 *    IMPLEMENTATION PRIVATE FUNCTIONS
 ****************************************************************************/

#ifdef XMALLOC_DEBUG

static void
my_init_hook (void)
{
        char *xmalloc_trace = getenv ("XMALLOC_TRACE");

        if (xmalloc_trace)
                fp = fopen (xmalloc_trace, "w");
  
        if (fp)
                fprintf (fp, "= Start\n");
}


static void
dump_info (char **strings, int cnt, char c, void *ptr, size_t n)
{
        int   i;
        char *string;
        char *tmp;
        char *end;
        char  ch;
        
        if (fp){
                string     = strings[1];
                tmp        = strchr (string, '[');

                ch         = *(tmp - 1);
                *(tmp - 1) = '\0';
                fprintf (fp, "@ %s:[", string);
                *(tmp - 1) = ch;

                end        = strchr (string, ']');
                *end       = '\0';
                fprintf (fp, "%s", tmp + 1);
                *end       = ']';
                for (i = 2; i < cnt; i++){
                        string = strings[i];
                        tmp    = strchr (string, '[');
                        end    = strchr (string, ']');
                        *end   = '\0';
                        fprintf (fp, ",%s", tmp + 1);
                        *end   = ']';
                }
                fprintf (fp, "] ");
                
                if (c == '+' || c == '>')
                        fprintf (fp, "%c 0x%08x 0x%08x\n", c,
                                 (unsigned) ptr, n);
                else
                        fprintf (fp, "%c 0x%08x\n", c, (unsigned) ptr);
        }
}


#endif

/****************************************************************************
 *    INTERFACE FUNCTIONS
 ****************************************************************************/


void *
xmalloc (size_t n)
{
#ifdef XMALLOC_DEBUG
        void    *array[1 + XMALLOC_DEPTH];
        size_t   s;
        char   **strings;
#endif
        void *p;

        if (n == 0)
                return NULL;
        p = malloc (n);

#ifdef XMALLOC_DEBUG
        if (fp){
                s       = backtrace (array, 1 + XMALLOC_DEPTH);
                strings = backtrace_symbols (array, s);

                dump_info (strings, s, '+', p, n);

                free (strings);
        }
#endif
  
        if (p == NULL)
                error (EXIT_FAILURE, errno, "malloc");
        return p;
}




void *
xcalloc (size_t n, size_t s)
{
#ifdef XMALLOC_DEBUG
        void    *array[1 + XMALLOC_DEPTH];
        size_t   cnt;
        char   **strings;
#endif
        void *p;

        if (n == 0 || s == 0)
                return NULL;
        p = calloc (n, s);

#ifdef XMALLOC_DEBUG
        if (fp){
                cnt     = backtrace (array, 1 + XMALLOC_DEPTH);
                strings = backtrace_symbols (array, cnt);

                dump_info (strings, cnt, '+', p, n * s);

                free (strings);
        }
#endif
  
        if (p == NULL)
                error (EXIT_FAILURE, errno, "calloc");
        return p;
}




void *
xrealloc (void *p, size_t n)
{
#ifdef XMALLOC_DEBUG
        void    *array[1 + XMALLOC_DEPTH];
        size_t   s;
        char   **strings;
#endif
        void *result;

        if (p == 0)
                return xmalloc (n);
        if (n == 0)
                return NULL;
        result = realloc (p, n);

#ifdef XMALLOC_DEBUG
        if (fp){
                s       = backtrace (array, 1 + XMALLOC_DEPTH);
                strings = backtrace_symbols (array, s);

                dump_info (strings, s, '<', p, 0);
                dump_info (strings, s, '>', result, n);

                free (strings);
        }                
#endif  
  
        if (result == NULL)
                error (EXIT_FAILURE, errno, "realloc");
        return result;
}





char *
xstrdup (const char *str)
{
#ifdef XMALLOC_DEBUG
        void    *array[1 + XMALLOC_DEPTH];
        size_t   s;
        char   **strings;
#endif
        char *p;

        if (str == NULL)
                return NULL;
        p = strdup (str);

#ifdef XMALLOC_DEBUG
        if (fp){
                s       = backtrace (array, 1 + XMALLOC_DEPTH);
                strings = backtrace_symbols (array, s);

                dump_info (strings, s, '+', p, strlen (str));

                free (strings);
        }
#endif  

        if (p == NULL)
                error (EXIT_FAILURE, errno, "strdup");
        return p;
}



void
xfree (void *ptr)
{
#ifdef XMALLOC_DEBUG
        void    *array[1 + XMALLOC_DEPTH];
        size_t   s;
        char   **strings;
#endif

        free (ptr);
  
#ifdef XMALLOC_DEBUG
        if (fp){
                s       = backtrace (array, 1 + XMALLOC_DEPTH);
                strings = backtrace_symbols (array, s);

                dump_info (strings, s, '-', ptr, 0);

                free (strings);
        }  
#endif
}


/****************************************************************************
 *
 *    END MODULE xmalloc.c
 *
 ****************************************************************************/
