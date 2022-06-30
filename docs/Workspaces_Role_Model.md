# Workspaces: Role Model application

The document assumes that you already now the basics or Role Model application in Complex Rest and are familiar with protected resource

# id

Every workspace and directory has **id** parameter.

This **id** parameter binds object in filesystem to **rest_auth** database, namely to **protected resource** via **object_id** field

For root, workspace **id** is an empty string. For other objects it is **UUID4**.

For now Role Model Management only works from Django admin site. To apply permissions you need to create/modify **protected resource**

# protected resource

It has the following fields:
- name (to be easily distinguishable from other protected resources)
- object_id (to bind to filesystem workspace or directory)
- owner (to know which rest user owns the protected resource)
- keychain (to know what permissions apply to the protected resource)

To add role model features to the object in filesystem, you need to bind its **id** to **protected resource object_id** via django admin site

# directory and workspace relation (protected resource inheritance)

If workspace has no protected resource it will inherit one from the closest parent directory for this workspace.

For instance `/root/parent/child/myworkspace.json`

If myworkspace.json has no protected resource and child directory has no protected resource but root and parent directories have protected resources,
parent directory protected resource will be applied to workspace

If child directory also had protected resource, child directory protected resource will be applied to workspace

If workspace is moved to root directory, root directory protected resource will be applied to workspace

If workspace has its own protected resource, it will be applied

# Root directory should always have a protected resource