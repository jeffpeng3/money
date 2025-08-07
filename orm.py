import uuid
from tortoise import fields, models

class Transaction(models.Model):
    id = fields.IntField(pk=True)
    description = fields.CharField(max_length=255)
    recorded_by_id = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.created_at.date()}{self.description}"

class LedgerEntry(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user_id = fields.IntField()
    amount = fields.IntField()
    transaction:Transaction = fields.ForeignKeyField("models.Transaction", related_name="entries", on_delete=fields.CASCADE) # type: ignore

    def __str__(self):
        return f"Transaction {self.transaction}: User {self.user_id} has amount {self.amount}"

    def __repr__(self) -> str:
        return self.__str__()