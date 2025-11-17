class Address():
    def __init__(self, street, number, city, postal_code, country):
        self.street = street
        self.number = number
        self.city = city
        self.postal_code = postal_code
        self.country = country

    def to_dict(self):
        return {
            "street": self.street,
            "number": self.number,
            "city": self.city,
            "postalCode": self.postal_code,
            "country": self.country
        }
    
    @staticmethod
    def from_dict(data):
        return Address(
            street=data.get('street'),
            number=data.get('number'),
            city=data.get('city'),
            postal_code=data.get('postalCode'),
            country=data.get('country')
        )