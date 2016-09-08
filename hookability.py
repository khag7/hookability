import sys
from functools import wraps
class plugins_can:

	h = {}

	def do_action(self,n,*a):
		return self.importall_hooked_functions(False,n,*a)

	def apply_filters(self,n,*a):
		return self.importall_hooked_functions(True,n,*a)

	def importall_hooked_functions(self,g,n,*a):
		a = list(a)
		if n in self.h:
			for p in sorted(self.h[n]):
				for f in self.h[n][p]:
					r = f(*a)
					a[0] = r if g else a[0]
			return a[0] if g else True
		return False
		
	def do_all(self,o):
		@self.do_before
		@self.filter_args
		@self.do_after
		@self.filter_return
		@self.replace
		@wraps(o)
		def wrapper(*a, **k):
			print '{}||{}'.format(o.__module__,o.__name__)
			return o(*a,**k)
		return wrapper

	def do_before(self,o):
		@wraps(o)
		def wrapper(*a, **k):
			self.do_action('before_{}||{}'.format(o.__module__,o.__name__),*a)
			return o(*a, **k)
		return wrapper

	def filter_args(self,o):
		@wraps(o)
		def wrapper(*a, **k):
			n = 'args_{}||{}'.format(o.__module__,o.__name__)
			if n in self.h:
				a = {self.apply_filters(n,*a)}
			return o(*a,**k)
		return wrapper
		
	def replace(self,o):
		@wraps(o)
		def wrapper(*a, **k):
			n = 'replace_{}||{}'.format(o.__module__,o.__name__)
			if n in self.h:
				return self.apply_filters(n,*a)
			else:
				return o(*a,**k)
		return wrapper

	def filter_return(self,o):
		@wraps(o)
		def wrapper(*a, **k):
			n = 'return_{}||{}'.format(o.__module__,o.__name__)
			r = o(*a,**k)
			if n in self.h:
				return self.apply_filters(n,r,*a)
			else:
				return r
		return wrapper

	def do_after(self,o):
		@wraps(o)
		def wrapper(*a, **k):
			r = o(*a, **k)
			self.do_action('after_{}||{}'.format(o.__module__,o.__name__),r,*a)
			return r
		return wrapper

can = plugins_can()

def add_filter(n,f,p=10):
	h = can.h
	h[n] = h.get(n,{})
	h[n][p] = h[n].get(p,[])
	h[n][p].append(f)

add_action = add_filter

def import_plugins( d = [] ):
	if d == []:
		from os.path import dirname
		d = [ dirname(sys.argv[0]), "plugins", "*.py" ]
	import glob
	from os.path import join, isfile
	for x in glob.glob(join(*d)):
		if isfile(x):
			execfile(x)

def import_and_hook_old( filepath = None ):
	global project
	import os
	import types
	import imp
	if filepath == None:
		sys.argv = sys.argv[1:]
		filepath = sys.argv[0]
	else:
		sys.argv[0] = filepath
	importpath = os.path.abspath(os.path.dirname(filepath))
	importfile = os.path.basename(filepath)[:-3]
	sys.path.append(importpath)
	os.chdir(importpath)
	try:
		project = __import__(importfile)
		sys.modules['project'] = project
	finally:
		del sys.path[-1]

	#auto decorate what was given to us
	for k,v in vars(project).items():
		if isinstance(v, types.FunctionType):
			vars(project)[k] = can.do_all(v)
			
	return project

def import_and_hook( filepath = None, *to_hook ):
	global project
	import os
	import types
	import imp
	
	# get cwd and arguments squared away and passed on
	if filepath == None:
		sys.argv = sys.argv[1:]
		filepath = sys.argv[0]
	else:
		sys.argv[0] = filepath
	importpath = os.path.abspath(os.path.dirname(filepath))
	importfile = os.path.basename(filepath)[:-3]
	sys.path.append(importpath)
	os.chdir(importpath)
	
	# we need to hook into all imports 
	class HookOnImport(object):
	
		def __init__(self, *args):
			self._cache = {}
			self.module_names = args

		def __enter__(self):
			sys.meta_path.insert(0, self)

		def __exit__(self, exc_type, exc_value, traceback):
			sys.meta_path.remove(self)

		def find_module(self, name, path=None):
			lastname = name.rsplit('.', 1)[-1]
			try:
				self._cache[name] = imp.find_module(lastname, path), path
			except ImportError:
				return
			return self
			
		def load_module(self, name):
			if name in sys.modules:
				return sys.modules[name]

			source, filename, newpath = self.get_source(name)
			(fd, fn, info), path = self._cache[name]

			if source is None:
				module = imp.load_module(name, fd, fn, info)
			else:
				fd, fn, info = imp.find_module(name.rsplit('.', 1)[-1], path)
				module = imp.load_module(name, fd, fn, info)
			
			if 1:#name in self.module_names:
									
				def decorate_all_children(parent, depth = 0):
					depth = depth + 1
					for k,v in vars(parent).items():
						if isinstance(v, types.FunctionType):
							vars(parent)[k] = can.do_all(v)
						else:
							if isinstance(v, types.ClassType):
								decorate_all_children( vars(parent)[k], depth )
							
				decorate_all_children(module)

			sys.modules[name] = module
			return module

		def get_source(self, name):
			try:
				(fd, fn, info), path = self._cache[name]
			except KeyError:
				raise ImportError(name)

			code = filename = newpath = None
			if info[2] == imp.PY_SOURCE:
				filename = fn
				with fd:
					code = fd.read()
			elif info[2] == imp.PY_COMPILED:
				filename = fn[:-1]
				with open(filename, 'U') as f:
					code = f.read()
			elif info[2] == imp.PKG_DIRECTORY:
				filename = os.path.join(fn, '__init__.py')
				newpath = [fn]
				with open(filename, 'U') as f:
					code = f.read()

			return code, filename, newpath

		def is_package(self, name):
			try:
				(fd, fn, info), path = self._cache[name]
			except KeyError:
				return False
			return info[2] == imp.PKG_DIRECTORY
		def old_find_module(self, name, path=None):
			if name in self.module_names:
				self.path = path
				return self
			return None
			
		def old_is_package(self, name):
			module_info = imp.find_module(name, self.path)
			return module_info[2][2] == imp.PKG_DIRECTORY
	
		def old_load_module(self, name):
			if name in sys.modules:
				return sys.modules[name]
			module_info = imp.find_module(name, self.path)
			module = imp.load_module(name, *module_info)
			for k,v in vars(module).items():
				if isinstance(v, types.FunctionType):
					vars(module)[k] = can.do_all(v)
			sys.modules[name] = module
			return module
			
	sys.meta_path = [HookOnImport(*to_hook)]
	
	# do the import
	try:
		project = __import__(importfile)
		sys.modules['project'] = project
	finally:
		del sys.path[-1]
	return project
	
if __name__ == '__main__':
	#load plugins
	import_plugins()
	
	#load passed argument
	project = import_and_hook()
	
	#initiate the loaded module
	project.main()