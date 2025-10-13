# unsatisfiable 

A project that can be used as a purposefully unsatisfiable dependency to force installation failure
for certain environments.

Generally you'll want to depend on this project via an environment marker. For example, if you
publish a Python library that does not support Windows you could add
`unsatisfiable; platform_system == "Windows"` to its dependencies.

