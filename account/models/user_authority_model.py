from django.db import models
from base.models.helpers.date_time_model import DateTimeModel

class UserAuthorityModel(DateTimeModel):
    authority = models.ForeignKey('account.AuthorityModel', on_delete=models.PROTECT)
    user = models.ForeignKey('account.UserModel', on_delete=models.PROTECT, related_name='user_authorities')
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_authority'
        unique_together = ('user', 'authority')