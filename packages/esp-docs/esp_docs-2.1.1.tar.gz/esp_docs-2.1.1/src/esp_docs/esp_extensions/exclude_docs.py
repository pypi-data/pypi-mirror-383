from sphinx.util.matching import get_matching_files


# Updates the excluded documents according to the conditional_include_dict {tag:documents}
def update_exclude_patterns(app, defines):
    # Default to building all if option not set
    if app.config.docs_to_build:
        build_subset(app, app.config)

    include_set = set()
    exclude_set = set()

    for tag, docs in app.config.conditional_include_dict.items():
        if not app.tags.has(tag):
            exclude_set.update(docs)
        else:
            include_set.update(docs)
    # Do not exclude docs that have been explicitly included, e.g. if a doc is listed in both
    # ESP32_DOCS and ESP32S2_DOCS it will be included for those targets.
    app.config.exclude_patterns.extend(exclude_set - include_set)


def build_subset(app, config):
    # Convert to list of docs to build
    docs_to_build = config.docs_to_build.split(',')

    # Exclude all documents which were not set as docs_to_build when build_docs were called
    exclude_docs = [filename for filename in get_matching_files(app.srcdir, exclude_patterns=docs_to_build)]

    app.config.exclude_patterns.extend(exclude_docs)
    docs = [filename for filename in get_matching_files(app.srcdir, exclude_patterns=exclude_docs)]
    # Get all docs that will be built
    if not docs:
        raise ValueError('No documents to build')
    print('Building a subset of the documents: {}'.format(docs))

    # Sphinx requires a master document, if there is a document name 'index' then we pick that
    index_docs = [doc for doc in docs if 'index' in doc]
    if index_docs:
        config.master_doc = index_docs[0].replace('.rst', '')
    else:
        config.master_doc = docs[0].replace('.rst', '')


def setup(app):
    # Tags are generated together with defines

    # Event emitted by build-system with a dict of defines created from the source files
    # e.g. {SOC_BT_SUPPORT: 1}
    # Used both by run_doxygen and exclude_docs
    app.add_event('defines-generated')

    app.connect('defines-generated', update_exclude_patterns)

    return {'parallel_read_safe': True, 'parallel_write_safe': True, 'version': '0.1'}
