# class AuthCovered(BaseProtectedResource):
#     """Provides interaction with Role Model"""
#
#     def __init__(self, *args, ids_chain: List[str] = None):
#         resources = {obj.object_id: obj for obj in ProtectedResource.objects.filter(object_id__in=ids_chain)}
#         res: Optional[ProtectedResource] = None
#         for _id in ids_chain:
#             res = resources.get(_id)
#             if res:
#                 break
#         if res:
#             super().__init__(keychain_id=res.keychain.pk, owner_id=res.owner.pk)
#         self.permissions = None




