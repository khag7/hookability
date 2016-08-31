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
			return o(*a,**k)
		return wrapper

	def do_before(self,o):
		@wraps(o)
		def wrapper(*a, **k):
			self.do_action('before_{}'.format(o.__name__),*a)
			return o(*a, **k)
		return wrapper

	def filter_args(self,o):
		@wraps(o)
		def wrapper(*a, **k):
			n = 'args_{}'.format(o.__name__)
			if n in self.h:
				a = {self.apply_filters(n,*a)}
			return o(*a,**k)
		return wrapper
		
	def replace(self,o):
		@wraps(o)
		def wrapper(*a, **k):
			n = 'replace_{}'.format(o.__name__)
			if n in self.h:
				return self.apply_filters(n,*a)
			else:
				return o(*a,**k)
		return wrapper

	def filter_return(self,o):
		@wraps(o)
		def wrapper(*a, **k):
			n = 'return_{}'.format(o.__name__)
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
			self.do_action('after_{}'.format(o.__name__),r,*a)
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
		import sys
		from os.path import dirname
		d = [ dirname(sys.argv[0]), "plugins", "*.py" ]
	import glob
	from os.path import join, isfile
	for x in glob.glob(join(*d)):
		if isfile(x):
			 execfile(x)
			 
if __name__ == '__main__':
    #load plugins
	importall()

	global project
	import os
	import types
	import imp
	import sys
	sys.path.append(os.path.dirname(sys.argv[1]))
	try:
		project = __import__(os.path.basename(sys.argv[1])[:-3])
		sys.modules['project'] = project
	finally:
		del sys.path[-1]

	#auto decorate what was given to us as arg 1
	for k,v in vars(project).items():
		if isinstance(v, types.FunctionType):
			vars(project)[k] = can.do_all(v)
	
	#initiate the loaded module
	print project.main()
