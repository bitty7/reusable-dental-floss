#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import json
from .config import get_raw_version

BRAVE_REPO = "brave/brave-browser"
BRAVE_CORE_REPO = "brave/brave-core"


def channels():
    return ['nightly', 'dev', 'beta', 'release']


def get_channel_display_name():
    raw = channels()
    d = {
        raw[0]: 'Nightly',
        raw[1]: 'Dev',
        raw[2]: 'Beta',
        raw[3]: 'Release'
    }

    return d[release_channel()]


def get_releases_by_tag(repo, tag_name, include_drafts=False):
    if include_drafts:
        return [r for r in repo.releases.get() if
                r['tag_name'] == tag_name]
    else:
        return [r for r in repo.releases.get() if
                r['tag_name'] == tag_name and not r['draft']]


def get_release(repo, tag, allow_published_release_updates=False):
    """
    allow_published_release_updates determines whether we will
    allow this process to update only a draft release, or will
    we also allow a published release to be updated.
    """
    release = None
    releases = get_releases_by_tag(repo, tag, include_drafts=True)
    if releases:
        print("[INFO] Found existing release draft")
        if len(releases) > 1:
            raise UserWarning("[INFO] More then one draft with the tag '{}' "
                              "found, not sure which one to merge with."
                              .format(tag))
        release = releases[0]
        if not allow_published_release_updates and not release['draft']:
            raise UserWarning("[INFO] Release with tag '{}' is already "
                              "published, aborting.".format(tag))

    return release


def release_channel():
    channel = os.environ['CHANNEL']
    message = ('Error: Please set the $CHANNEL '
               'environment variable, which is your release channel')
    assert channel, message
    return channel


def get_tag():
    return 'v' + get_raw_version() + release_channel()


def release_name():
    return '{0} Channel'.format(get_channel_display_name())


def retry_func(try_func, catch, retries, catch_func=None):
    for count in range(0, retries + 1):
        try:
            ret = try_func(count)
            break
        except catch as e:
            print('[ERROR] Caught exception {}, {} retries left. {}'.format(
                catch, count, e.message))
            if catch_func:
                catch_func(count)
            if count >= retries:
                raise e
    return ret