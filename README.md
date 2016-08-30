# EXPLANATION OF SHORTHAND VARIABLES USED
	# n = name of filter or action
	# f = filtering function to execute
	# p = priority of execution of functions
	# o = original function passed when using decorator
	# h = hooks dictionary (all filter/action hooks to be executed)
	# a = arguments to pass to function
	# k = kw arguments to pass to function
	# g = filtering (as opposed to actioning)
	# r = retunred statement from filtering function
	# d = directory path to search for plugin files (include *.py), as a list to be separated by filestystem separator symbol

#HOW TO USE
	# if you are familiar with wordpress, its like their plugins api
	# include this module in your script using import plugins
	# call plugins.execute() very early in your script
	# to allow plugins to alter an object in your script, wrap them like this:
		# the_object = apply_filters('name_of_filter',the_object,data_to_pass_1,data_to_pass_2,...)
	# or allow plugins to execute arbitrary actions at various points in your script like this:
		# do_action('name_of_action',data_to_pass_1,data_to_pass_2,...)
	# or use decorators on your functions like @plugins.can.replace or @plugins.can.do_before or @plugins.can.filter_args
	# and users can add their own *.py plugin files in the plugins folder using either add_action or add_filter:
		# add_filter('name_of_filter',plugin_function_for_filtering)
		# def plugin_function_for_filtering(item_to_filter,data_to_pass_1,data_to_pass_2: 
			# [put code and return the new value]
			# return new_value_for_item
			# [if doing 'add_action' return is ignored]


