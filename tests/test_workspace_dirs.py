
#     def test_update_workspace_title_in_root(self):
#         title = 'root_ws'
#         new_title = 'sw_toor'
#         content = 'root_ws_content'
#         ws_id = self.root_dir.accessed_by(self.admin).create_workspace(workspace_conf={
#             "title": title,
#             "content": content})
#         ws = TWorkspace(uid=ws_id, path='').accessed_by(self.admin)
#         data = ws.read()
#         self.assertAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
#         time.sleep(1)
#         ws.update(_conf={"title": new_title})
#         data = ws.read()
#         self.assertNotAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
#         self.assertEqual(ws_id, data['id'])
#         self.assertEqual('', data['path'])
#         self.assertEqual(new_title, data['title'])
#         self.assertEqual(content, data['content'])
#         self.assertEqual(False, data['is_dir'])
#
#     def test_update_workspace_content_in_root(self):
#         title = 'root_ws'
#         content = 'root_ws_content'
#         new_content = 'tnetnoc_sw_toor'
#         ws_id = self.root_dir.accessed_by(self.admin).create_workspace(workspace_conf={
#             "title": title,
#             "content": content})
#         ws = TWorkspace(uid=ws_id, path='').accessed_by(self.admin)
#         data = ws.read()
#         self.assertAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
#         time.sleep(1)
#         ws.update(_conf={"content": new_content})
#         data = ws.read()
#         self.assertNotAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
#         self.assertEqual(ws_id, data['id'])
#         self.assertEqual('', data['path'])
#         self.assertEqual(title, data['title'])
#         self.assertEqual(new_content, data['content'])
#         self.assertEqual(False, data['is_dir'])
#
#     def test_update_workspace_in_root(self):
#         title = 'root_ws'
#         new_title = 'sw_toor'
#         content = 'root_ws_content'
#         new_content = 'tnetnoc_sw_toor'
#         ws_id = self.root_dir.accessed_by(self.admin).create_workspace(workspace_conf={
#             "title": title,
#             "content": content})
#         ws = TWorkspace(uid=ws_id, path='').accessed_by(self.admin)
#         data = ws.read()
#         self.assertAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
#         time.sleep(1)
#         ws.update(_conf={"title": new_title, "content": new_content})
#         data = ws.read()
#         self.assertNotAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
#         self.assertEqual(ws_id, data['id'])
#         self.assertEqual('', data['path'])
#         self.assertEqual(new_title, data['title'])
#         self.assertEqual(new_content, data['content'])
#         self.assertEqual(False, data['is_dir'])
#
#     def test_update_workspace_title(self):
#         title = 'dir_ws'
#         new_title = 'sw_rid'
#         content = 'dir_ws_content'
#         parent_title = 'in_root_dir'
#         self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": parent_title})
#         in_root_dir = TDirectory(path=utils.encode_name(parent_title))
#         ws_id = in_root_dir.accessed_by(self.admin).create_workspace(workspace_conf={
#             "title": title,
#             "content": content})
#         ws = TWorkspace(uid=ws_id, path=utils.encode_name(parent_title)).accessed_by(self.admin)
#         data = ws.read()
#         self.assertAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
#         time.sleep(1)
#         ws.update(_conf={"title": new_title})
#         data = ws.read()
#         self.assertNotAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
#         self.assertEqual(ws_id, data['id'])
#         self.assertEqual(parent_title, data['path'])
#         self.assertEqual(new_title, data['title'])
#         self.assertEqual(content, data['content'])
#         self.assertEqual(False, data['is_dir'])
#
#     def test_update_workspace_content(self):
#         title = 'dir_ws'
#         content = 'dir_ws_content'
#         new_content = 'tnetnoc_sw_rid'
#         parent_title = 'in_root_dir'
#         self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": parent_title})
#         in_root_dir = TDirectory(path=utils.encode_name(parent_title))
#         ws_id = in_root_dir.accessed_by(self.admin).create_workspace(workspace_conf={
#             "title": title,
#             "content": content})
#         ws = TWorkspace(uid=ws_id, path=utils.encode_name(parent_title)).accessed_by(self.admin)
#         ws.update(_conf={"content": new_content})
#         data = ws.read()
#         self.assertAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
#         time.sleep(1)
#         ws.update(_conf={"content": new_content})
#         data = ws.read()
#         self.assertNotAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
#         self.assertEqual(ws_id, data['id'])
#         self.assertEqual(parent_title, data['path'])
#         self.assertEqual(title, data['title'])
#         self.assertEqual(new_content, data['content'])
#         self.assertEqual(False, data['is_dir'])
#
#     def test_update_workspace(self):
#         title = 'dir_ws'
#         new_title = 'sw_rid'
#         content = 'dir_ws_content'
#         new_content = 'tnetnoc_sw_rid'
#         parent_title = 'in_root_dir'
#         self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": parent_title})
#         in_root_dir = TDirectory(path=utils.encode_name(parent_title))
#         ws_id = in_root_dir.accessed_by(self.admin).create_workspace(workspace_conf={
#             "title": title,
#             "content": content})
#         ws = TWorkspace(uid=ws_id, path=utils.encode_name(parent_title)).accessed_by(self.admin)
#         data = ws.read()
#         self.assertAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
#         time.sleep(1)
#         ws.update(_conf={"title": new_title, "content": new_content})
#         data = ws.read()
#         self.assertNotAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
#         self.assertEqual(ws_id, data['id'])
#         self.assertEqual(parent_title, data['path'])
#         self.assertEqual(new_title, data['title'])
#         self.assertEqual(new_content, data['content'])
#         self.assertEqual(False, data['is_dir'])
#
#     def test_update_directory_in_root(self):
#         title = 'in_root_dir'
#         new_title = 'rid_toor_ni'
#         self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": title})
#         in_root_dir = TDirectory(path=utils.encode_name(title))
#         in_root_dir.update(_conf={"new_title": new_title})
#         data = in_root_dir.read()
#         self.assertEqual(new_title, data['path'])
#         self.assertEqual(new_title, data['title'])
#         self.assertEqual(True, data['is_dir'])
#
#     def test_update_directory(self):
#         title = "dir_inside_another_dir"
#         new_title = 'rid_rethona_edisni_rid'
#         parent_title = 'in_root_dir'
#         self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": parent_title})
#         in_root_dir = TDirectory(path=utils.encode_name(parent_title))
#         in_root_dir.accessed_by(self.admin).create_dir(_conf={"title": title, "dir": None})
#         dr = TDirectory(path=utils.encode_name(f"{parent_title}/{title}")).accessed_by(self.admin)
#         dr.update(_conf={"new_title": new_title})
#         data = dr.read()
#         self.assertEqual(f"{parent_title}/{new_title}", data['path'])
#         self.assertEqual(new_title, data['title'])
#         self.assertEqual(True, data['is_dir'])
#
#     def test_move_workspace_from_root_and_back(self):
#         title = "moving_ws"
#         content = 'discontent'
#         dir_title = 'in_root_dir'
#         self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": dir_title})
#         ws_id = self.root_dir.accessed_by(self.admin).create_workspace(workspace_conf={
#             "title": title,
#             "content": content})
#         ws = TWorkspace(uid=ws_id, path='').accessed_by(self.admin)
#         old_path = ws.filesystem_path.parent
#         ws.update(_conf={"new_path": dir_title})
#         new_path = ws.filesystem_path.parent
#         data = ws.read()
#         self.assertEqual(ws_id, data['id'])
#         self.assertEqual(dir_title, data['path'])
#         self.assertEqual(title, data['title'])
#         self.assertEqual(content, data['content'])
#         self.assertEqual(False, data['is_dir'])
#         self.assertEqual(len(list(old_path.glob('*.json'))), 0)  # no workspace at old path
#         self.assertEqual(len(list(new_path.glob('*.json'))), 1)
#         ws.update(_conf={"new_path": ""})
#         data = ws.read()
#         self.assertEqual(ws_id, data['id'])
#         self.assertEqual("", data['path'])
#         self.assertEqual(title, data['title'])
#         self.assertEqual(content, data['content'])
#         self.assertEqual(False, data['is_dir'])
#         self.assertEqual(len(list(old_path.glob('*.json'))), 1)  # workspace back at old path
#         self.assertEqual(len(list(new_path.glob('*.json'))), 0)
#
#     def test_move_workspace_far_from_root_and_back(self):
#         title = "moving_ws"
#         content = 'discontent'
#         parent_dir_title = 'in_root_dir'
#         dir_title = 'next_dir'
#         self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": parent_dir_title})
#         in_root_dir = TDirectory(path=utils.encode_name(parent_dir_title))
#         in_root_dir.accessed_by(self.admin).create_dir(_conf={"title": dir_title})
#         ws_id = self.root_dir.accessed_by(self.admin).create_workspace(workspace_conf={
#             "title": title,
#             "content": content})
#         ws = TWorkspace(uid=ws_id, path='').accessed_by(self.admin)
#         old_path = ws.filesystem_path.parent
#         ws.update(_conf={"new_path": f"{parent_dir_title}/{dir_title}"})
#         new_path = ws.filesystem_path.parent
#         data = ws.read()
#         self.assertEqual(ws_id, data['id'])
#         self.assertEqual(f"{parent_dir_title}/{dir_title}", data['path'])
#         self.assertEqual(title, data['title'])
#         self.assertEqual(content, data['content'])
#         self.assertEqual(False, data['is_dir'])
#         self.assertEqual(len(list(old_path.glob('*.json'))), 0)  # no workspace at old path
#         self.assertEqual(len(list(new_path.glob('*.json'))), 1)
#         ws.update(_conf={"new_path": ""})
#         data = ws.read()
#         self.assertEqual(ws_id, data['id'])
#         self.assertEqual("", data['path'])
#         self.assertEqual(title, data['title'])
#         self.assertEqual(content, data['content'])
#         self.assertEqual(False, data['is_dir'])
#         self.assertEqual(len(list(old_path.glob('*.json'))), 1)  # workspace back at old path
#         self.assertEqual(len(list(new_path.glob('*.json'))), 0)
#
#     def test_move_workspace(self):
#         title = "moving_ws"
#         content = 'discontent'
#         source_dir = 'src'
#         destination_dir = 'dst'
#         self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": source_dir})
#         self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": destination_dir})
#         src = TDirectory(path=utils.encode_name(source_dir))
#         ws_id = src.accessed_by(self.admin).create_workspace(workspace_conf={
#             "title": title,
#             "content": content})
#         ws = TWorkspace(uid=ws_id, path=utils.encode_name(source_dir))
#         old_path = ws.filesystem_path.parent
#         ws.update(_conf={"new_path": destination_dir})
#         new_path = ws.filesystem_path.parent
#         data = ws.read()
#         self.assertEqual(ws_id, data['id'])
#         self.assertEqual(destination_dir, data['path'])
#         self.assertEqual(title, data['title'])
#         self.assertEqual(content, data['content'])
#         self.assertEqual(False, data['is_dir'])
#         self.assertEqual(len(list(old_path.glob('*.json'))), 0)  # no workspace at old path
#         self.assertEqual(len(list(new_path.glob('*.json'))), 1)
#         ws.update(_conf={"new_path": source_dir})
#         data = ws.read()
#         self.assertEqual(ws_id, data['id'])
#         self.assertEqual(source_dir, data['path'])
#         self.assertEqual(title, data['title'])
#         self.assertEqual(content, data['content'])
#         self.assertEqual(False, data['is_dir'])
#         self.assertEqual(len(list(old_path.glob('*.json'))), 1)  # workspace back at old path
#         self.assertEqual(len(list(new_path.glob('*.json'))), 0)
#
#     def test_move_directory_from_root_and_back(self):
#         title = "moving_dir"
#         dir_title = 'in_root_dir'
#         self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": dir_title})
#         self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": title})
#         dr = TDirectory(path=utils.encode_name(title)).accessed_by(self.admin)
#         old_path = dr.filesystem_path.parent
#         dr.update(_conf={"new_path": dir_title})
#         new_path = dr.filesystem_path.parent
#         data = dr.read()
#         self.assertEqual(f"{dir_title}/{title}", data['path'])
#         self.assertEqual(title, data['title'])
#         self.assertEqual(True, data['is_dir'])
#         self.assertEqual(len(list(old_path.glob('*'))), 2)  # no directory at old path
#         self.assertEqual(len(list(new_path.glob('*'))), 2)
#         dr.update(_conf={"new_path": ""})
#         data = dr.read()
#         self.assertEqual(title, data['path'])
#         self.assertEqual(title, data['title'])
#         self.assertEqual(True, data['is_dir'])
#         self.assertEqual(len(list(old_path.glob('*'))), 3)  # directory back at old path
#         self.assertEqual(len(list(new_path.glob('*'))), 1)
#
#     def test_move_directory_far_from_root_and_back(self):
#         title = "moving_dir"
#         dir_title = 'in_root_dir'
#         next_dir = "next_dir"
#         self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": dir_title})
#         self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": title})
#         in_root_dir = TDirectory(path=utils.encode_name(dir_title)).accessed_by(self.admin)
#         in_root_dir.create_dir(_conf={"title": next_dir})
#         dr = TDirectory(path=utils.encode_name(title)).accessed_by(self.admin)
#         old_path = dr.filesystem_path.parent
#         dr.update(_conf={"new_path": f"{dir_title}/{next_dir}"})
#         new_path = dr.filesystem_path.parent
#         data = dr.read()
#         self.assertEqual(f"{dir_title}/{next_dir}/{title}", data['path'])
#         self.assertEqual(title, data['title'])
#         self.assertEqual(True, data['is_dir'])
#         self.assertEqual(len(list(old_path.glob('*'))), 2)  # no directory at old path
#         self.assertEqual(len(list(new_path.glob('*'))), 2)
#         dr.update(_conf={"new_path": ""})
#         data = dr.read()
#         self.assertEqual(title, data['path'])
#         self.assertEqual(title, data['title'])
#         self.assertEqual(True, data['is_dir'])
#         self.assertEqual(len(list(old_path.glob('*'))), 3)  # directory back at old path
#         self.assertEqual(len(list(new_path.glob('*'))), 1)
#
#     def test_move_directory(self):
#         title = "moving_dir"
#         source_dir = 'src'
#         destination_dir = 'dst'
#         self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": source_dir})
#         self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": destination_dir})
#         src = TDirectory(path=utils.encode_name(source_dir))
#         src.accessed_by(self.admin).create_dir(_conf={"title": title})
#         dr = TDirectory(path=utils.encode_name(f"{source_dir}/{title}")).accessed_by(self.admin)
#         old_path = dr.filesystem_path.parent
#         dr.update(_conf={"new_path": destination_dir})
#         new_path = dr.filesystem_path.parent
#         data = dr.read()
#         self.assertEqual(f"{destination_dir}/{title}", data['path'])
#         self.assertEqual(title, data['title'])
#         self.assertEqual(True, data['is_dir'])
#         self.assertEqual(len(list(old_path.glob('*'))), 1)  # no directory at old path
#         self.assertEqual(len(list(new_path.glob('*'))), 2)
#         dr.update(_conf={"new_path": source_dir})
#         data = dr.read()
#         self.assertEqual(f"{source_dir}/{title}", data['path'])
#         self.assertEqual(title, data['title'])
#         self.assertEqual(True, data['is_dir'])
#         self.assertEqual(len(list(old_path.glob('*'))), 2)  # directory back at old path
#         self.assertEqual(len(list(new_path.glob('*'))), 1)
#
#     def test_move_dir_inside_itself(self):
#         dir_title = 'in_root_dir'
#         next_dir = "next_dir"
#         self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": dir_title})
#         in_root_dir = TDirectory(path=utils.encode_name(dir_title)).accessed_by(self.admin)
#         in_root_dir.create_dir(_conf={"title": next_dir})
#         try:
#             in_root_dir.update(_conf={"new_path": f"{dir_title}/{next_dir}"})
#             self.assertTrue(False, 'dir somehow was moved inside itself')
#         except DirectoryContentException:
#             self.assertTrue(True)
#
#     def test_delete_workspace_in_root(self):
#         title = 'deleteme'
#         content = 'dark secrets'
#         ws_id = self.root_dir.accessed_by(self.admin).create_workspace(workspace_conf={
#             "title": title,
#             "content": content})
#         ws = TWorkspace(uid=ws_id, path='')
#         ws.accessed_by(self.admin).delete()
#         self.assertEqual(len(list(self.root_dir.filesystem_path.glob('*.json'))), 0)
#
#     def test_delete_workspace(self):
#         title = 'deleteme'
#         content = 'dark secrets'
#         dir_title = 'in_root_dir'
#         self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": dir_title})
#         in_root_dir = TDirectory(path=utils.encode_name(dir_title)).accessed_by(self.admin)
#         ws_id = in_root_dir.accessed_by(self.admin).create_workspace(workspace_conf={
#             "title": title,
#             "content": content})
#         ws = TWorkspace(uid=ws_id, path=utils.encode_name(dir_title))
#         ws.accessed_by(self.admin).delete()
#         self.assertEqual(len(list(in_root_dir.filesystem_path.glob('*.json'))), 0)
#
#     def test_delete_directory_in_root(self):
#         title = 'deleteme'
#         content = 'dark secrets'
#         dir_title = 'in_root_dir'
#         next_dir = "next_dir"
#         self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": dir_title})
#         in_root_dir = TDirectory(path=utils.encode_name(dir_title)).accessed_by(self.admin)
#         in_root_dir.accessed_by(self.admin).create_workspace(workspace_conf={
#             "title": title,
#             "content": content})
#         in_root_dir.accessed_by(self.admin).create_workspace(workspace_conf={
#             "title": title + '0',
#             "content": content + '0'})
#         in_root_dir.create_dir(_conf={"title": next_dir})
#         self.assertEqual(len(list(self.root_dir.filesystem_path.rglob('*'))), 7)
#         in_root_dir.delete()
#         self.assertEqual(len(list(self.root_dir.filesystem_path.rglob('*'))), 1)
#
#     def test_delete_directory(self):
#         title = 'deleteme'
#         content = 'dark secrets'
#         dir_title = 'in_root_dir'
#         next_dir = "next_dir"
#         self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": dir_title})
#         in_root_dir = TDirectory(path=utils.encode_name(dir_title)).accessed_by(self.admin)
#         in_root_dir.create_dir(_conf={"title": next_dir})
#         dr = TDirectory(path=utils.encode_name(f"{dir_title}/{next_dir}")).accessed_by(self.admin)
#         dr.accessed_by(self.admin).create_workspace(workspace_conf={
#             "title": title,
#             "content": content})
#         dr.accessed_by(self.admin).create_workspace(workspace_conf={
#             "title": title + '0',
#             "content": content + '0'})
#         self.assertEqual(len(list(self.root_dir.filesystem_path.rglob('*'))), 7)
#         dr.delete()
#         self.assertEqual(len(list(self.root_dir.filesystem_path.rglob('*'))), 3)
#
#     def test_reserved_meta_file_name(self):
#         dir_title = self.root_dir.dir_metafile_name
#         try:
#             self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": dir_title})
#             self.assertTrue(False, 'dir with meta filename somehow was created')
#         except DirectoryContentException:
#             self.assertTrue(True)
#
#     def test_dir_exists(self):
#         dir_title = 'in_root_dir'
#         self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": dir_title})
#         try:
#             self.root_dir.accessed_by(self.admin).create_dir(_conf={"title": dir_title})
#             self.assertTrue(False, 'dir already existed but somehow created again')
#         except DirectoryContentException:
#             self.assertTrue(True)
#
#     def tearDown(self) -> None:
#         rmtree(self.tmp_path, ignore_errors=True)
#         rmtree(self.base_path, ignore_errors=True)
