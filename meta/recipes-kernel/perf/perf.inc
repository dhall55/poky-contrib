def perf_arch_supports_feature(feature, trueval, falseval, d):
    """
    Check which perf features a particular architecture supports.

    The perf_features_by_arch table below lists the perf features
    supported by each arch.  If you want a particular arch to support
    a given set of perf features, add an entry for the arch to this
    table.  Otherwise the arch won't support any features (which may
    be exactly what you want, just a barebones perf without any extra
    baggage, which is what you get if you don't add any features
    here.)

    Available perf features:
      perf-scripting: enable support for Perl and Python bindings
      perf-tui: enable support for the perf TUI (via libnewt)

    """
    perf_features_by_arch = {
	"core2":      "perf-scripting perf-tui",
	"core2-64":   "perf-scripting perf-tui",
	"x86":	      "perf-scripting perf-tui",
	"x86-64":     "perf-scripting perf-tui",
	"i586":	      "perf-scripting perf-tui",
	}

    tune = d.getVar("DEFAULTTUNE", True) or ""
    if perf_features_by_arch.has_key(tune):
	if feature in perf_features_by_arch[tune]:
		return trueval
    return falseval
