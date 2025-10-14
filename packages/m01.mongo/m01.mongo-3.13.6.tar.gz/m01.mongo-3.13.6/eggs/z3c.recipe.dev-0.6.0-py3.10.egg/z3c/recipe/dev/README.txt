=====================
Z3 development recipe
=====================

z3c.recipe.dev app
------------------

This Zope 3 recipes allows you to define Zope applications.

The 'app' recipe can be used to define a Zope application. It is designed to
work with with Zope solely from eggs. The app recipe causes a part to be
created. The part will contain the application's `zope.conf`, `site.zcml`,
`principals.zcml` and `securitypolicy.zcml`. This configuration files will get
recreated during each update. Another folder called logs will get created and
contains the `access.log` and `z3c.log` files. This log files doesn't get
recreated. The start script itself is located in the bin folder and uses the
configuration files from the relevant parts folder.


Options
~~~~~~~

The 'app' recipe accepts the following options:

eggs
  The names of one or more eggs, with their dependencies that should
  be included in the Python path of the generated scripts.

server
  The ``zserver`` or ``twisted`` server otpion.

zope.conf
  The contents of zope.conf.

site.zcml
  The contents of site.zcml.

principals.zcml
  The contents of securitypolicy.zcml.

securitypolicy.zcml
  The contents of securitypolicy.zcml.

site.zcml
  The contents of site.zcml.


Test
~~~~

Lets define some (bogus) eggs that we can use in our application:

  >>> mkdir('demo1')
  >>> write('demo1', 'setup.py',
  ... '''
  ... from setuptools import setup
  ... setup(name = 'demo1')
  ... ''')

  >>> mkdir('demo2')
  >>> write('demo2', 'setup.py',
  ... '''
  ... from setuptools import setup
  ... setup(name = 'demo2', install_requires='demo1')
  ... ''')

We'll create a `buildout.cfg` file that defines our application:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... develop = demo1 demo2
  ... parts = myapp var
  ... newest = false
  ...
  ... [myapp]
  ... recipe = z3c.recipe.dev:app
  ... eggs = demo2
  ...        z3c.recipe.dev [test]
  ... server = zserver
  ... zope.conf = ${var:zconfig}
  ...   <eventlog>
  ...     #level DEBUG
  ...     <logfile>
  ...       path STDOUT
  ...       formatter zope.exceptions.log.Formatter
  ...     </logfile>
  ...   </eventlog>
  ...
  ...   devmode on
  ...
  ... site.zcml =
  ...     <include package="demo1" />
  ...     <include package="demo2" />
  ...
  ... principals.zcml =
  ...   <unauthenticatedPrincipal
  ...       id="zope.anybody"
  ...       title="Unauthenticated User"
  ...       />
  ...
  ...   <unauthenticatedGroup
  ...       id="zope.Anybody"
  ...       title="Unauthenticated Users"
  ...       />
  ...
  ...   <authenticatedGroup
  ...       id="zope.Authenticated"
  ...       title="Authenticated Users"
  ...       />
  ...
  ...   <everybodyGroup
  ...       id="zope.Everybody"
  ...       title="All Users"
  ...       />
  ...
  ...   <principal
  ...       id="zope.manager"
  ...       title="Manager"
  ...       login="Manager"
  ...       password="password"
  ...       />
  ...
  ...   <grant
  ...       role="zope.Manager"
  ...       principal="zope.manager"
  ...       />
  ...
  ... securitypolicy.zcml =
  ...   <include package="zope.app.securitypolicy" />
  ...
  ...   <securityPolicy
  ...       component="zope.app.securitypolicy.zopepolicy.ZopeSecurityPolicy"
  ...       />
  ...
  ...   <role id="zope.Anonymous" title="Everybody"
  ...       description="All users have this role implicitly" />
  ...   <role id="zope.Manager" title="Site Manager" />
  ...   <role id="zope.Member" title="Site Member" />
  ...
  ...   <!-- Replace the following directive if you don't want public access -->
  ...   <grant permission="zope.View"
  ...        role="zope.Anonymous"
  ...        />
  ...   <grant permission="zope.app.dublincore.view"
  ...        role="zope.Anonymous"
  ...        />
  ...
  ...   <grantAll role="zope.Manager" />
  ...
  ... [var]
  ... recipe = zc.recipe.filestorage
  ...
  ... ''' % globals())

Now, Let's run the buildout and see what we get:

  >>> print system(join('bin', 'buildout')),
  Develop: '/sample-buildout/demo1'
  Develop: '/sample-buildout/demo2'
  Installing var.
  Installing myapp.
  Generated script '/sample-buildout/bin/myapp'.

The bin folder contains the start script:

  >>> ls('bin')
  -  buildout-script.py
  -  buildout.exe
  -  myapp-script.py
  -  myapp.exe

The myapp-scrip.py contains the start code for our zope setup:

  >>> cat('bin', 'myapp')
  #!"C:\Python24\python.exe"
  <BLANKLINE>
  import sys
  sys.path[0:0] = [
    '/sample-buildout/demo2',
    '/z3c.recipe.dev/trunk/src',
    '/sample-buildout/eggs/zc.recipe.filestorage-1.0.1-py2.4.egg',
    '/sample-buildout/eggs/zope.testing-3.7.1-py2.4.egg',
    '/sample-buildout/eggs/zc.recipe.egg-1.1.0-py2.4.egg',
    '/sample-buildout/eggs/zc.buildout-1.1.1-py2.4.egg',
    '/sample-pyN.N.egg',
    '/sample-buildout/eggs/zconfig-2.6.1-py2.4.egg',
    '/sample-buildout/demo1',
    '/sample-buildout/eggs/zope.interface-3.5.0-py2.4-win32.egg',
    '/sample-pyN.N.egg',
    ]
  <BLANKLINE>
  import os
  sys.argv[0] = os.path.abspath(sys.argv[0])
  <BLANKLINE>
  <BLANKLINE>
  import zope.app.server.main
  <BLANKLINE>
  if __name__ == '__main__':
      zope.app.server.main.main([
    '-C', '/sample-buildout/parts/myapp/zope.conf',
    ]+sys.argv[1:])

And the myapp folder contains the configure files:

  >>> ls('parts', 'myapp')
  -  principals.zcml
  -  securitypolicy.zcml
  -  site.zcml
  -  zope.conf


z3c.recipe.dev script
---------------------

The script recipe allows us to point to scripts which the recipe will install
a execute script hook for us. You can use this if you need to run a python
script which knows about some egg packages.


Options
~~~~~~~

The 'script' recipe accepts the following options:

eggs
  The names of one or more eggs, with their dependencies that should
  be included in the Python path of the generated scripts.

module
  The ``module`` which contains the ``method`` to be executed.

method
  The ``method`` which get called from the ``module``.

arguments
  Use the option ``arguments`` to pass arguments to the script.
  All the string will be copied to the script 1:1.
  So what you enter here is what you get.

environment
  The environement if needed by your script


Test
~~~~

Lets define a egg that we can use in our application:

  >>> mkdir('hello')
  >>> write('hello', 'setup.py',
  ... '''
  ... from setuptools import setup
  ... setup(name='hello')
  ... ''')

And let's define a python module which we use for our test:

  >>> write('hello', 'helloworld.py',
  ... """
  ... def helloWorld(*args):
  ...     print 'Hello World'
  ...     for a in args:
  ...         print a
  ... """)

Alos add a `__init__` to the `hello` package:

  >>> write('hello', '__init__.py', '#make package')

We'll create a `buildout.cfg` file that defines our script:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... develop = hello
  ... parts = helloworld
  ... newest = false
  ...
  ... [helloworld]
  ... recipe = z3c.recipe.dev:script
  ... eggs = hello
  ... module = helloworld
  ... method = helloWorld
  ...
  ... ''' % globals())

Let's run buildout again:

  >>> print system(join('bin', 'buildout')),
  Develop: '/sample-buildout/hello'
  Uninstalling myapp.
  Uninstalling var.
  Installing helloworld.
  Generated script '/sample-buildout/bin/helloworld'.

And check the script again. Now we see the `helloWorld()` method is used:

  >>> cat('bin', 'helloworld')
  #!C:\Python24\python.exe
  <BLANKLINE>
  import sys
  sys.path[0:0] = [
    '/sample-buildout/hello',
    ]
  <BLANKLINE>
  import os
  sys.argv[0] = os.path.abspath(sys.argv[0])
  <BLANKLINE>
  <BLANKLINE>
  import helloworld
  <BLANKLINE>
  if __name__ == '__main__':
      helloworld.helloWorld()

Now we can call the script:

  >>> print system(join('bin', 'helloworld')),
  Hello World


Test with parameters
--------------------

Of the same script defined above.

Use the option ``arguments = `` to pass arguments to the script.
All the string will be copied to the script ``1:1``.
So what you enter here is what you get.

We'll create a ``buildout.cfg`` file that defines our script:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... develop = hello
  ... parts = helloworld
  ... newest = false
  ...
  ... [helloworld]
  ... recipe = z3c.recipe.dev:script
  ... eggs = hello
  ... module = helloworld
  ... method = helloWorld
  ... arguments = 'foo', 'bar'
  ...
  ... ''' % globals())

Let's run buildout again:

  >>> print system(join('bin', 'buildout')),
  Develop: '/sample-buildout/hello'
  Uninstalling helloworld.
  Installing helloworld.
  Generated script '/sample-buildout/bin/helloworld'.

And check the script again. Now we see the `helloWorld()` method is used:

  >>> cat('bin', 'helloworld')
  #!C:\Python24\python.exe
  <BLANKLINE>
  import sys
  sys.path[0:0] = [
    '/sample-buildout/hello',
    ]
  <BLANKLINE>
  import os
  sys.argv[0] = os.path.abspath(sys.argv[0])
  <BLANKLINE>
  <BLANKLINE>
  import helloworld
  <BLANKLINE>
  if __name__ == '__main__':
      helloworld.helloWorld('foo', 'bar')

Now we can call the script:

  >>> print system(join('bin', 'helloworld')),
  Hello World
  foo
  bar


Creating Directories
--------------------

  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = data-dir
  ... find-links = http://download.zope.org/distribution
  ... newest = false
  ...
  ... [data-dir]
  ... recipe = z3c.recipe.dev:mkdir
  ... path = mystuff
  ... """)
  >>> print system(buildout),
  Uninstalling helloworld.
  Installing data-dir.
  data-dir: Creating directory mystuff

  >>> ls(sample_buildout)
  -  .installed.cfg
  d  bin
  -  buildout.cfg
  d  demo1
  d  demo2
  d  develop-eggs
  d  eggs
  d  hello
  d  mystuff
  d  parts

If we change the directory name the old directory ('mystuff') is not deleted.

  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = data-dir
  ... find-links = http://download.zope.org/distribution
  ... newest = false
  ...
  ... [data-dir]
  ... recipe = z3c.recipe.dev:mkdir
  ... path = otherdir
  ... """)
  >>> print system(buildout),
  Uninstalling data-dir.
  Installing data-dir.
  data-dir: Creating directory otherdir

  >>> ls(sample_buildout)
  -  .installed.cfg
  d  bin
  -  buildout.cfg
  d  demo1
  d  demo2
  d  develop-eggs
  d  eggs
  d  hello
  d  mystuff
  d  otherdir
  d  parts

We can also create a full path.

  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = data-dir
  ... find-links = http://download.zope.org/distribution
  ... newest = false
  ...
  ... [data-dir]
  ... recipe = z3c.recipe.dev:mkdir
  ... path = with/subdir
  ... """)
  >>> print system(buildout),
  data-dir: Cannot create /sample-buildout/with/subdir. /sample-buildout/with is not a directory.
  While:
    Installing.
    Getting section data-dir.
    Initializing part data-dir.
  Error: Invalid Path

But we need to activate this function explicitely.

  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = data-dir
  ... find-links = http://download.zope.org/distribution
  ... newest = false
  ...
  ... [data-dir]
  ... recipe = z3c.recipe.dev:mkdir
  ... createpath = True
  ... path = with/subdir
  ... """)
  >>> print system(buildout),
  Uninstalling data-dir.
  Installing data-dir.
  data-dir: Creating directory with/subdir

  >>> ls(sample_buildout)
  -  .installed.cfg
  d  bin
  -  buildout.cfg
  d  demo1
  d  demo2
  d  develop-eggs
  d  eggs
  d  hello
  d  mystuff
  d  otherdir
  d  parts
  d  with


Creating Files
--------------

The mkfile recipe creates a file with a given path, content and
permissions.

  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = script
  ... newest = false
  ...
  ... [script]
  ... recipe = z3c.recipe.dev:mkfile
  ... path = file.sh
  ... content = hoschi
  ... mode = 0755
  ... """)
  >>> print system(buildout)
  Uninstalling data-dir.
  Installing script.
  script: Writing file /sample-buildout/file.sh
  <BLANKLINE>

  >>> ls(sample_buildout)
  -  .installed.cfg
  d  bin
  -  buildout.cfg
  d  demo1
  d  demo2
  d  develop-eggs
  d  eggs
  -  file.sh
  d  hello
  d  mystuff
  d  otherdir
  d  parts
  d  with

The content is written to the file.

  >>> cat(sample_buildout, 'file.sh')
  hoschi

And the mode is set. Note set a mode is not supported on windows

  >>> import os, stat, sys
  >>> path = os.path.join(sample_buildout, 'file.sh')
  >>> if sys.platform[:3].lower() != "win":
  ...     oct(stat.S_IMODE(os.stat(path)[stat.ST_MODE]))
  ... else:
  ...     '0755'
  '0755'

If we change the filename the old file is deleted.

  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = script
  ... newest = false
  ...
  ... [script]
  ... recipe = z3c.recipe.dev:mkfile
  ... path = newfile.sh
  ... content = hoschi
  ... mode = 0755
  ... """)
  >>> print system(buildout)
  Uninstalling script.
  Installing script.
  script: Writing file /sample-buildout/newfile.sh
  <BLANKLINE>

  >>> ls(sample_buildout)
  -  .installed.cfg
  d  bin
  -  buildout.cfg
  d  demo1
  d  demo2
  d  develop-eggs
  d  eggs
  d  hello
  d  mystuff
  -  newfile.sh
  d  otherdir
  d  parts
  d  with

We can also specify to create the path for the file.

  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = script
  ... newest = false
  ...
  ... [script]
  ... recipe = z3c.recipe.dev:mkfile
  ... createpath = On
  ... path = subdir/for/file/file.sh
  ... content = hoschi
  ... mode = 0755
  ... """)
  >>> print system(buildout)
  Uninstalling script.
  Installing script.
  script: Creating directory /sample-buildout/subdir/for/file
  script: Writing file /sample-buildout/subdir/for/file/file.sh
  <BLANKLINE>

  >>> ls(sample_buildout + '/subdir/for/file')
  -  file.sh


