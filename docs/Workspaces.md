# Workspaces and the way of organizing them

## Directories

Previously you were able to save workspaces only in a special workspaces root folder specified in dtcd_workspaces.conf section [workspaces] base_path

Now you have the opportunity to create dirs inside this directory and place your workspaces there

## How it works

In the endpoint url you can now specify the path to directory you are interested in. The path will be concatenated with special workspaces root folder (configured in workspace.base_path)

For obvious reasons **workspace_path** should be encoded in url safe base64

`'workspace/object/<path:workspace_path>'`

Please always add slash after `'workspace/object'`
___
- GET: 

By default, lists all workspaces and directories' info in **workspace_path** directory. Info doesn't return workspace content! ("content": null)

Info contains:
1. id
2. path
3. title
4. creation_time (unix timestamp)
5. modification_time (unix timestamp)
6. is_dir (bool flag)
7. plugin (plugin name)

To get content as well you need to specify one workspace in your query. For that add workspace **id** as a query string parameter. Example: `?id=c3fffa8a-2ac8-4225-a44d-ebb339f916f7`

To avoid listing and get **workspace_path** directory info add **dir** query string parameter. Example: `?dir`

If both **dir** and **id** are provided, **id** will be ignored

You can get root workspace directory info (but you can't rename it or move via API)
___
- POST: 

To create workspace you need to specify it as json dictionary inside an array. As a response POST will return the same info, but with id generated for this workspace. Example: `[{"title":"myworkspace", "content": "123"}]`

To create directory you need to specify it as json dictionary inside an array and add special key **dir**. As a response POST will return the same info. Example: `[{"title":"myfolder", "dir": null}]`

Both directories and workspaces will be created in **workspace_path** directory (if it doesn't exist the error will occur)
___
- PUT: 

PUT has 2 use cases:

1. Rename:

For workspaces works as POST but requires id. You can change either title or content or both. Returns array with id of changed workspace. Example: `[{"title":"yourworkspace", "content": "789", "id":"c3fffa8a-2ac8-4225-a44d-ebb339f916f7"}]`
If id not provided API will try to change **workspace_path** directory title. For that you need to provide **new_title** key (it doesn't have to be encoded). Example `[{"new_title":"yourfolder"}]`

2. Move:

If **new_path** key for **workspace** is provided, other keys will be ignored and move workspace from **workspace_path** directory into new_path directory will be attempted.

Workspace example `[{"id":"3c2a2d56-ce69-491d-825c-d2ace374460f", "new_path": ""}]` - moves workspace with id 3c2a2d56-ce69-491d-825c-d2ace374460f from **workspace_path** directory into root directory

Workspace example `[{"id":"3c2a2d56-ce69-491d-825c-d2ace374460f", "new_path": "parent/child"}]` - moves workspace with id 3c2a2d56-ce69-491d-825c-d2ace374460f from **workspace_path** directory into parent/child (parent is in root directory)

If **new_path** key for **directory** is provided, other keys will be ignored and move **workspace_path** directory into new_path directory will be attempted.

Workspace example `[{"new_path": ""}]` - moves **workspace_path** directory into root directory

Workspace example `[{"new_path": "parent/child"}]` - moves **workspace_path** directory into parent/child (parent is in root directory)
___
- DELETE:

For **workspaces** requires the id of the workspace inside array. This workspace will be searched for in **workspace_path** directory and deleted. Example: `["c3fffa8a-2ac8-4225-a44d-ebb339f916f7"]`

For **directories** will delete **workspace_path** directory
___
## Note: 

- All the directories should be created explicitly!
- For security reasons **//** or **..** are not allowed in **workspace_path**
