import datetime
'''
1. Класс Client
- 👤 ФИО, ID, статус
- 🔢 список номеров счетов
- 📞 контакты
- ✅ проверка возраста >= 18
'''

class Client:
    def __init__(self, full_name, client_id, date_of_birth, status="active", accounts=None, contacts=None):
        self._validate_age(date_of_birth)
        self.full_name = full_name
        self.client_id = client_id
        self.date_of_birth = date_of_birth
        self.status = status
        self.accounts = accounts if accounts is not None else []
        self.contacts = contacts if contacts is not None else []

    def _validate_age(self, date_of_birth):
        if not isinstance(date_of_birth, datetime.date):
            raise TypeError("Date of birth must be a datetime.date object")
        age = datetime.date.today().year - date_of_birth.year
        if age < 18:
            raise ValueError("Client must be at least 18 years old.")   
        
    def add_account(self, account):
        """Добавляет счет клиенту."""
        self.accounts.append(account)

    def remove_account(self, account):
        """Удаляет счет клиента."""
        if account in self.accounts:
            self.accounts.remove(account)