def paginate(rc, limit, func, page):
    offset = page * limit
    objects, count_remain = func(limit, offset)

    p = Page()
    p.has_older = count_remain > 0
    p.has_newer = offset > 0

    rc           = rc()
    urls         = rc.get('urls')
    endpoint     = rc.get('endpoint')
    args         = rc.get('args').copy()

    if p.has_newer:
        if page == 1:
            # We have this exception so that we don't use ?page=0
            p.newer = urls.build(endpoint, args, force_external=True)
        else:
            n_args = args.copy()
            n_args['page'] = page - 1
            p.newer = urls.build(endpoint, n_args, force_external=True)
    else:
        p.newer = None

    if p.has_older:
        n_args = args.copy()
        n_args['page'] = page + 1
        p.older = urls.build(endpoint, n_args, force_external=True)
    else:
        p.older = None

    return objects, p


class Page(object):

    __slots__ = ['has_older', 'has_newer', 'newer', 'older']
