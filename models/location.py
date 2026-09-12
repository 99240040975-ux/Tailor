from datetime import datetime
from models import db


class State(db.Model):
    __tablename__ = 'states'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    code = db.Column(db.String(10), nullable=True, index=True)  # e.g. 'TN' or '33'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    districts = db.relationship('District', backref='state', cascade='all, delete-orphan', lazy='dynamic')
    tailors = db.relationship('Tailor', backref='state', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code
        }

    def __repr__(self):
        return f'<State {self.name} ({self.code})>'


class District(db.Model):
    __tablename__ = 'districts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    state_id = db.Column(db.Integer, db.ForeignKey('states.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    code = db.Column(db.String(20), nullable=True, index=True)  # LGD District Code
    census_code = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    taluks = db.relationship('Taluk', backref='district', cascade='all, delete-orphan', lazy='dynamic')
    cities = db.relationship('City', backref='district', cascade='all, delete-orphan', lazy='dynamic')
    towns = db.relationship('Town', backref='district', cascade='all, delete-orphan', lazy='dynamic')
    villages = db.relationship('Village', backref='district', cascade='all, delete-orphan', lazy='dynamic')
    tailors = db.relationship('Tailor', backref='district', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'state_id': self.state_id,
            'name': self.name,
            'code': self.code
        }

    def __repr__(self):
        return f'<District {self.name}>'


class Taluk(db.Model):
    __tablename__ = 'taluks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    code = db.Column(db.String(20), nullable=True, index=True)  # LGD Sub-district Code
    census_code = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    cities = db.relationship('City', backref='taluk', lazy='dynamic')
    towns = db.relationship('Town', backref='taluk', lazy='dynamic')
    villages = db.relationship('Village', backref='taluk', cascade='all, delete-orphan', lazy='dynamic')
    tailors = db.relationship('Tailor', backref='taluk', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'district_id': self.district_id,
            'name': self.name,
            'code': self.code
        }

    def __repr__(self):
        return f'<Taluk {self.name}>'


class City(db.Model):
    __tablename__ = 'cities'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id', ondelete='CASCADE'), nullable=False, index=True)
    taluk_id = db.Column(db.Integer, db.ForeignKey('taluks.id', ondelete='SET NULL'), nullable=True, index=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    code = db.Column(db.String(20), nullable=True, index=True)  # Localbody Code
    localbody_type = db.Column(db.String(50), nullable=True)  # Corporation, Municipality
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    towns = db.relationship('Town', backref='city', lazy='dynamic')
    localities = db.relationship('Locality', backref='city', lazy='dynamic')
    tailors = db.relationship('Tailor', backref='city_rel', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'district_id': self.district_id,
            'taluk_id': self.taluk_id,
            'name': self.name,
            'code': self.code,
            'type': self.localbody_type
        }

    def __repr__(self):
        return f'<City {self.name}>'


class Town(db.Model):
    __tablename__ = 'towns'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id', ondelete='CASCADE'), nullable=False, index=True)
    taluk_id = db.Column(db.Integer, db.ForeignKey('taluks.id', ondelete='SET NULL'), nullable=True, index=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id', ondelete='SET NULL'), nullable=True, index=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    code = db.Column(db.String(20), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    villages = db.relationship('Village', backref='town', lazy='dynamic')
    localities = db.relationship('Locality', backref='town', lazy='dynamic')
    tailors = db.relationship('Tailor', backref='town', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'district_id': self.district_id,
            'taluk_id': self.taluk_id,
            'city_id': self.city_id,
            'name': self.name,
            'code': self.code
        }

    def __repr__(self):
        return f'<Town {self.name}>'


class Village(db.Model):
    __tablename__ = 'villages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id', ondelete='CASCADE'), nullable=False, index=True)
    taluk_id = db.Column(db.Integer, db.ForeignKey('taluks.id', ondelete='CASCADE'), nullable=False, index=True)
    town_id = db.Column(db.Integer, db.ForeignKey('towns.id', ondelete='SET NULL'), nullable=True, index=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    code = db.Column(db.String(20), nullable=True, index=True)  # LGD Village Code
    census_code = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    localities = db.relationship('Locality', backref='village', lazy='dynamic')
    tailors = db.relationship('Tailor', backref='village', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'district_id': self.district_id,
            'taluk_id': self.taluk_id,
            'town_id': self.town_id,
            'name': self.name,
            'code': self.code
        }

    def __repr__(self):
        return f'<Village {self.name}>'


class Locality(db.Model):
    __tablename__ = 'localities'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id', ondelete='SET NULL'), nullable=True, index=True)
    town_id = db.Column(db.Integer, db.ForeignKey('towns.id', ondelete='SET NULL'), nullable=True, index=True)
    village_id = db.Column(db.Integer, db.ForeignKey('villages.id', ondelete='SET NULL'), nullable=True, index=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    pincode = db.Column(db.String(10), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'pincode': self.pincode,
            'city_id': self.city_id,
            'town_id': self.town_id,
            'village_id': self.village_id
        }

    def __repr__(self):
        return f'<Locality {self.name} ({self.pincode})>'
