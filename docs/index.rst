Welcome to lbry-rocksdb-ng's documentation!
==========================================

Overview
--------
Python bindings to the C++ interface of http://rocksdb.org/ using cython::

    import rocksdb
    db = rocksdb.DB("test.db", rocksdb.Options(create_if_missing=True))
    db.put(b"a", b"b")
    print db.get(b"a")


This community-maintained fork is independent of LBRY Inc.
The current Linux wheel tests cover CPython 3.9 and 3.13 with RocksDB 6.25.3.
The Python import remains ``rocksdb``.

.. toctree::
    :maxdepth: 2

    Instructions how to install <installation>
    Tutorial <tutorial/index>
    API <api/index>
    Changelog <changelog>


Contributing
------------

Source can be found on `github <https://github.com/kodxana/lbry-rocksdb-ng>`_.
Feel free to fork and send pull-requests or create issues on the
`github issue tracker <https://github.com/kodxana/lbry-rocksdb-ng/issues>`_

RoadMap/TODO
------------

No plans so far. Please submit wishes to the github issues.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
