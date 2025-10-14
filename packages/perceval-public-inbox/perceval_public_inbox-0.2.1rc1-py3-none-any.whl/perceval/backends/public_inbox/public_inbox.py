# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Jose Javier Merchante <jjmerchante@bitergia.com>
#

import email
import logging
import os
import re

from grimoirelab_toolkit.datetime import str_to_datetime, InvalidDateError

from ...backend import (BackendCommand,
                        BackendCommandArgumentParser)
from ...backends.core.git import (Git,
                                  GitRepository)
from ...errors import ParseError
from ...utils import (DEFAULT_DATETIME,
                      DEFAULT_LAST_DATETIME,
                      message_to_dict)


CATEGORY_MESSAGE = 'message'

logger = logging.getLogger(__name__)


class PublicInbox(Git):
    """PublicInbox backend for Perceval.

    This class retrieves the email messages stored in one public-inbox
    mirror repository. Initialize this class passing the directory path
    of the repository where the file is stored. The origin of the data
    will be set to the value of `uri`.

    :param uri: URI of the public-inbox; typically, the URL of their
    mailing list
    :param gitpath: directory path of the public-inbox repository
    :param tag: label used to mark the data
    :param archive: archive to store/retrieve items
    """
    version = '0.1.0'

    CATEGORIES = [CATEGORY_MESSAGE]

    DATE_FIELD = 'Date'
    MESSAGE_ID_FIELD = 'Message-ID'

    def __init__(self, uri, gitpath, tag=None, archive=None):
        # Initialize the backend using the Git backend
        super().__init__(uri, gitpath, tag=tag, archive=archive)

    def fetch(self, category=CATEGORY_MESSAGE, from_date=DEFAULT_DATETIME, to_date=DEFAULT_LAST_DATETIME,
              latest_items=False):
        """Fetch the messages from a public-inbox local repository.

        The method retrieves, from a public-inbox repository, the messages stored
        in each commit.

        :param category: the category of items to fetch
        :param from_date: obtain messages since this date
        :param to_date: obtain messages until this date
        :param latest_items: sync with the repository to fetch only the
            newest commits

        :returns: a generator of messages
        """
        items = super().fetch(category=category,
                              from_date=from_date, to_date=to_date,
                              latest_items=latest_items,
                              no_update=True)

        return items

    def fetch_items(self, category, **kwargs):
        """Fetch the messages.

        :param category: the category of items to fetch
        :param kwargs: backend arguments

        :returns: a generator of items
        """
        from_date = kwargs['from_date']
        to_date = kwargs['to_date']

        logger.info("Looking for messages from '%s' on '%s' since %s until %s",
                    self.uri, self.gitpath, str(from_date), str(to_date))

        repo = PublicInboxRepository(self.uri, self.gitpath)

        commits = super().fetch_items(category, **kwargs)

        for commit in commits:
            try:
                raw_msg = repo.file_contents(commit['commit'], 'm')
                msg = email.message_from_string(raw_msg)
                message = message_to_dict(msg)
            except (ParseError, UnicodeEncodeError) as e:
                logger.warning(f"Error parsing commit {commit['commit']}; skipping")
                continue

            if not self._validate_message(message):
                logger.warning(f"Message from commit <{commit['commit']}> is invalid")
                continue

            message = self._casedict_to_dict(message)

            yield message

        logger.info("Fetch process completed")

    def _fetch_newest_commits_from_repo(self, repo):
        if not repo.has_alternates():
            return super()._fetch_newest_commits_from_repo(repo)

        # The repository has alternate objects and new commits can't
        # be fetched directly from there, fetch the newest commits
        # from alternate objects repositories.
        repo = PublicInboxRepository(self.uri, self.gitpath)
        for repo_gitpath, repo_uri in repo.alternate_repos():
            logger.info("Fetching latest commits: '%s' git repository",
                        repo_uri)

            gitrepo = GitRepository(repo_uri, repo_gitpath)
            hashes = gitrepo.sync()
            if not hashes:
                continue

            gitshow = repo.show(hashes)
            for commit in self.parse_git_log_from_iter(gitshow):
                yield commit

    @classmethod
    def has_archiving(cls):
        """Returns whether it supports archiving items on the fetch process.

        :returns: this backend does not support items archive
        """
        return False

    @classmethod
    def has_resuming(cls):
        """Returns whether it supports to resume the fetch process.

        :returns: this backend supports items resuming
        """
        return True

    @staticmethod
    def metadata_id(item):
        """Extracts the identifier from a message item."""

        return str(item[PublicInbox.MESSAGE_ID_FIELD])

    @staticmethod
    def metadata_updated_on(item):
        """Extracts the update time from a message item.

        The timestamp is extracted from 'Date' field.
        This date is converted to UNIX timestamp format.

        :param item: item generated by the backend

        :returns: a UNIX timestamp
        """
        ts = item[PublicInbox.DATE_FIELD]
        ts = str_to_datetime(ts)

        return ts.timestamp()

    @staticmethod
    def metadata_category(item):
        """Extracts the category from a message item.

        This backend only generates one type of item which is
        'message'.
        """
        return CATEGORY_MESSAGE

    def metadata(self, item, filter_classified=False):
        """Public Inbox metadata.

        This method takes items, overriding `metadata` decorator.
        Ignore Git implementation of metadata() and use the parent.

        :param item: an item fetched by a backend
        :param filter_classified: sets if classified fields were filtered
        """
        item = super(Git, self).metadata(item, filter_classified=filter_classified)

        return item

    def _init_client(self, from_archive=False):
        pass

    def _validate_message(self, message):
        """Check if the given message has the mandatory fields"""

        # This check is "case insensitive" because we're
        # using 'CaseInsensitiveDict' from requests.structures
        # module to store the contents of a message.
        if self.MESSAGE_ID_FIELD not in message:
            logger.warning("Field 'Message-ID' not found in message %s; ignoring",
                           message['unixfrom'])
            return False

        if not message[self.MESSAGE_ID_FIELD]:
            logger.warning("Field 'Message-ID' is empty in message %s; ignoring",
                           message['unixfrom'])
            return False

        if self.DATE_FIELD not in message:
            logger.warning("Field 'Date' not found in message %s; ignoring",
                           message['unixfrom'])
            return False

        if not message[self.DATE_FIELD]:
            logger.warning("Field 'Date' is empty in message %s; ignoring",
                           message['unixfrom'])
            return False

        try:
            str_to_datetime(message[self.DATE_FIELD])
        except InvalidDateError:
            logger.warning("Invalid date %s in message %s; ignoring",
                           message[self.DATE_FIELD], message['unixfrom'])
            return False

        return True

    def _casedict_to_dict(self, message):
        """Convert a message in CaseInsensitiveDict to dict.

        This method also converts well known problematic headers,
        such as Message-ID and Date to a common name.
        """
        message_id = message.pop(self.MESSAGE_ID_FIELD)
        date = message.pop(self.DATE_FIELD)

        msg = {k: v for k, v in message.items()}
        msg[self.MESSAGE_ID_FIELD] = message_id
        msg[self.DATE_FIELD] = date

        return msg


class PublicInboxCommand(BackendCommand):
    """Class to run PublicInbox backend from the command line."""

    BACKEND = PublicInbox

    @classmethod
    def setup_cmd_parser(cls):
        """Returns the PublicInbox argument parser."""

        parser = BackendCommandArgumentParser(cls.BACKEND,
                                              from_date=True,
                                              to_date=True)
        # Required arguments
        parser.parser.add_argument('uri',
                                   help="URI of the public-inbox, usually the URL to their mailing list")
        parser.parser.add_argument('gitpath',
                                   help="Path to the public-inbox repository")
        # Optional arguments
        group = parser.parser.add_argument_group('Git arguments')
        group.add_argument('--latest-items', dest='latest_items',
                           action='store_true',
                           help="Fetch latest commits added to the repository")

        return parser


class PublicInboxRepository(GitRepository):
    """Manage a public-inbox repository.

    This class extends the GitRepository class. Thus, it provides some
    additional commands such as `ls_tree`, `cat_file` or `file_contents`.

    :param uri: URI of the repository
    :param dirpath: local directory where the repository is stored
    """
    LS_TREE_PATTERN = r"""^(?P<mode>\d+)[ \t]+
                           (?P<type>\w+)[ \t]+
                           (?P<object>\w+)[ \t]+
                           (?P<file>\w+)"""
    GIT_LS_TREE_BLOB_FILE = re.compile(LS_TREE_PATTERN, re.VERBOSE)

    def alternate_repos(self):
        """Obtain the list of the alternate repositories and its remote

        :return: list of tuples that contains repositories' absolute path
            and remote URL.
        """
        repos = []
        alternates = os.path.join(self.dirpath, 'objects/info/alternates')
        if not os.path.exists(alternates):
            return repos

        with open(alternates) as f:
            for repo_objects in f:
                repo_relative = os.path.dirname(repo_objects)
                gitpath = os.path.normpath(os.path.join(self.dirpath, 'objects', repo_relative))
                uri = self._remote_repository(gitpath)
                repos.append((gitpath, uri))

        return repos

    def _remote_repository(self, gitpath):
        """Obtain the remote repository from a git path

        :param gitpath: path of a repository

        :return: Repository URLs origin
        """
        cmd_config = ['git', 'config', 'remote.origin.url']
        outs = self._exec(cmd_config, cwd=gitpath, env=self.gitenv)
        return outs.decode('utf-8').strip()

    def ls_tree(self, commit, file):
        """List the contents of a tree object.

        :param commit: the hash of a commit
        :param file: name of the file

        :return: a line with information of the file
        """
        cmd_ls_tree = ['git', 'ls-tree', commit, file]
        outs = self._exec(cmd_ls_tree, cwd=self.dirpath, env=self.gitenv)
        return outs.decode('utf-8')

    def cat_file(self, obj):
        """Provide content for repository blob objects.

        :param obj: the name of the object to show

        :return: raw contents of the object
        """
        cmd_cat_file = ['git', 'cat-file', 'blob', obj]
        contents = self._exec(cmd_cat_file, cwd=self.dirpath, env=self.gitenv)
        return contents.decode('utf-8', errors='surrogateescape')

    def file_contents(self, commit, file):
        """Shows the plain contents of a file in a given commit.

        :param commit: the hash of a commit
        :param file: name of the file

        :return: raw contents of the file
        """
        line = self.ls_tree(commit, file)
        m = self.GIT_LS_TREE_BLOB_FILE.match(line)
        if not m:
            msg = f"blob object not found for file '{file}' in commit '{commit}'"
            raise ParseError(cause=msg)
        blob = m.group('object')

        return self.cat_file(blob)
