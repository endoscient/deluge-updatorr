from copy import deepcopy
from deluge._libtorrent import lt

# Torrent tracker handler classes registry.
TRACKER_HANDLERS = {}


def get_registered_handlers(domain=None):
    """Returns registered handlers dictionary."""
    if domain is None:
        return TRACKER_HANDLERS
    return TRACKER_HANDLERS.get(domain)


def get_tracker_handler(torrent_data, logger):
    """Returns an appropiate torrent tracker handler object
    from handlers dictionary basing on resource_url."""
    for host_name in TRACKER_HANDLERS.keys():
        if host_name in torrent_data['comment']:
            return TRACKER_HANDLERS[host_name](host_name, torrent_data, logger)
    return None


def read_torrent_file(filepath):
    """Reads torrent file from filesystem and returns its contents."""
    f = open(filepath, 'rb')
    contents = f.read()
    f.close()
    return contents


def read_torrent_info(file_contents):
    """Returns a dictionary with basic information from torrent
    contents (see `read_torrent_file()`).

    Dict keys:
        hash - Torrent hash.
        files - A list of files within the torrent.

    """
    info_contents = lt.torrent_info(lt.bdecode(file_contents))
    files_from_torrent = [a_file.path for a_file in info_contents.files()]
    info = {'hash': str(info_contents.info_hash()), 'files': files_from_torrent}
    return info


def get_new_prefs(full_prefs, new_torrent_info):
    """Returns a dictionary with preferences for a new torrent session.
    Those preferences are deduces from full preferences of previous
    session of that torrent.

    Those files that were marked as "not to download" in previous session
    whold have the same priority in a new one. Basically all files priorities
    are copied from the previous session.

    """
    new_prefs = deepcopy(full_prefs)

    # These are some items we definitely do not want in a new session.
    info_to_drop = (
        'comment', 'hash', 'peers', 'progress', 'num_seeds', 'ratio', 'total_peers', 'total_wanted',
        'distributed_copies', 'time_added', 'active_time', 'next_announce',
        'tracker', 'tracker_host', 'tracker_status', 'trackers',
        'files', 'file_priorities', 'file_progress', 'num_files',
        'is_seed', 'seed_rank', 'seeding_time', 'download_payload_rate', 'message',
        'num_peers', 'compact', 'total_uploaded', 'total_done', 'num_pieces',
        'total_payload_download', 'total_seeds', 'piece_length', 'all_time_download',
        'name', 'seeds_peers_ratio', 'eta', 'is_finished', 'total_size', 'state', 'upload_payload_rate',
        )

    for pref_name in info_to_drop:
        if pref_name in new_prefs:
            del new_prefs[pref_name]

    new_prefs['download_location'] = new_prefs['save_path']
    new_prefs['mapped_files'] = {}
    new_prefs['file_priorities'] = []

    # Copying files priorities.
    old_priorities = get_files_priorities(full_prefs)
    for a_file in new_torrent_info['files']:
        priority = 1
        if a_file in old_priorities:
            priority = old_priorities[a_file]
        new_prefs['file_priorities'].append(priority)

    return new_prefs


def get_files_priorities(torrent_data):
    """Returns a dictionary with files priorities, where
    filepaths are keys, and priority identifiers are values."""
    files = {}
    walk_counter = 0
    for file in torrent_data['files']:
        files[file['path']] = torrent_data['file_priorities'][walk_counter]
        walk_counter += 1
    return  files