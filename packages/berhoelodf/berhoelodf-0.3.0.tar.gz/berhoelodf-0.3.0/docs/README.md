# berhoelODF

Lightweight and limited access to odf files using lxml.

It is just used by me for a limited project of converting a
spreadsheet to ``Django`` data. For me this package works much faster
than ``odfpy``. Just loading my 5.7MB ods file took 1.5 minutes. This
package is based on ``lxml``, and ``lxml`` parses the XML in 2
seconds, the whole processing to ``Django`` takes about 1.5 minutes.

If you have other requirements, the code should be easily extensible.

## Installation

```console
$> pip install berhoelodf
```

### Availability

The latest version should be available at my [GitLab](<https://gitlab.com/berhoel/python/berhoelODF.git>) repository, the
package is avaliable at [pypi](<https://pypi.org/project/berhoelODF/>)
via `pip install berhoelodf`.

### Documentation

Documentation is hosted on [höllmanns.de](<https://python.höllmanns.de/berhoelODF/>).
