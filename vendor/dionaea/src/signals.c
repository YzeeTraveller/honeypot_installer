/**
 * This file is part of the dionaea honeypot
 *
 * SPDX-FileCopyrightText: 2009 Paul Baecher & Markus Koetter
 *
 * SPDX-License-Identifier: GPL-2.0-or-later
 */

#include "config.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <ev.h>
#include <glib.h>
#ifdef HAVE_EXECINFO_H
#include <execinfo.h>
#endif


#include "dionaea.h"
#include "signals.h"
#include "modules.h"
#include "log.h"

#define D_LOG_DOMAIN "log"

void sigint_cb(struct ev_loop *loop, struct ev_signal *w, int revents)
{
	g_warning("%s loop %p w %p revents %i",__PRETTY_FUNCTION__, loop, w, revents);
	ev_break(loop, EVBREAK_ALL);
}

void sigterm_cb(struct ev_loop *loop, struct ev_signal *w, int revents)
{
	g_warning("%s loop %p w %p revents %i",__PRETTY_FUNCTION__, loop, w, revents);
	ev_break(loop, EVBREAK_ALL);
}

void sighup_cb(struct ev_loop *loop, struct ev_signal *w, int revents)
{
  /* ToDo
	g_warning("%s loop %p w %p revents %i",__PRETTY_FUNCTION__, loop, w, revents);

	g_info("Reloading config");
	if( (g_dionaea->config.config = lcfg_new(g_dionaea->config.name)) == NULL )
	{
		g_critical("config not found");
	}

	if( lcfg_parse(g_dionaea->config.config) != lcfg_status_ok )
	{
		g_critical("lcfg error: %s\n", lcfg_error_get(g_dionaea->config.config));
	}

	g_dionaea->config.root = lcfgx_tree_new(g_dionaea->config.config);


	// modules ...
	modules_hup();

	// loggers hup
	for( GList *it = g_dionaea->logging->loggers; it != NULL; it = it->next )
	{
		struct logger *l = it->data;
		g_message("Logger %p hup %p", l, l->log);
		if( l->hup != NULL )
			l->hup(l, l->data);
	}
  */
}



void sigsegv_cb(struct ev_loop *loop, struct ev_signal *w, int revents)
//int segv_handler(int sig)
{
	g_warning("%s loop %p w %p revents %i",__PRETTY_FUNCTION__, loop, w, revents);
//	g_warning("%s sig %i",__PRETTY_FUNCTION__, sig);
	char cmd[100];

	snprintf(cmd, sizeof(cmd), "%s/bin/dionaea-backtrace %d > /tmp/segv_dionaea.%d.out 2>&1",
			 PREFIX, (int)getpid(), (int)getpid());
	if( system(cmd) )
		return;
	signal(SIGSEGV, SIG_DFL);
//	return 0;
}


void sigsegv_backtrace_cb(int sig)
{
#ifdef HAVE_EXECINFO_H
#define BACKTRACE_SIZE 32
	void *back[BACKTRACE_SIZE];
	size_t size;

	size = backtrace( back, BACKTRACE_SIZE );

	g_mutex_lock(&g_dionaea->logging->lock);
	for( GList *it = g_dionaea->logging->loggers; it != NULL; it = it->next )
	{
		struct logger *l = it->data;

		if( l->fd == -1 )
			continue;

		if( l->flush != NULL )
			l->flush(l, l->data);
		const char *msg =
			"\n"
			"This is the end.\n"
			"This software just had a segmentation fault.\n"
			"The bug you encountered may even be exploitable.\n"
			"If you want to assist in fixing the bug, please create a new issue on GitHub and append the backtrace.\n"
			"You can create better backtraces with gdb, for more information visit https://github.com/DinoTools/dionaea\n"
			"Once you read this message, your tty may be broken, simply type reset, so it will come to life again\n"
			"\n";
		if( write(l->fd, msg, strlen(msg)) != strlen(msg))
			continue;
		backtrace_symbols_fd(back, size, l->fd);
	}
//	g_mutex_unlock(&g_dionaea->logging->lock);
#endif
	exit(-1);
}
