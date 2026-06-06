from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class Officer(UserMixin, db.Model):
    __tablename__ = 'officers'

    officer_id    = db.Column(db.Integer, primary_key=True)
    badge_number  = db.Column(db.String(20), unique=True, nullable=False)
    full_name     = db.Column(db.String(120), nullable=False)
    rank          = db.Column(db.String(60), nullable=False)
    station       = db.Column(db.String(100), nullable=False)
    username      = db.Column(db.String(60), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active     = db.Column(db.Boolean, default=True, nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    offences_issued   = db.relationship('Offence', backref='officer', lazy=True)
    payments_received = db.relationship('Payment', backref='receiving_officer', lazy=True)
    audit_entries     = db.relationship('AuditLog', backref='officer', lazy=True)

    def get_id(self):
        return str(self.officer_id)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Driver(db.Model):
    __tablename__ = 'drivers'

    driver_id      = db.Column(db.Integer, primary_key=True)
    national_id    = db.Column(db.String(30), unique=True, nullable=False)
    full_name      = db.Column(db.String(120), nullable=False)
    date_of_birth  = db.Column(db.Date, nullable=True)
    licence_number = db.Column(db.String(30), unique=True, nullable=False)
    licence_class  = db.Column(db.String(20), nullable=False)
    licence_expiry = db.Column(db.Date, nullable=False)
    passport_photo = db.Column(db.String(255), nullable=True)
    licence_scan   = db.Column(db.String(255), nullable=True)
    phone_number   = db.Column(db.String(20), nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    owned_vehicles = db.relationship('Vehicle', backref='registered_owner', lazy=True)
    offences       = db.relationship('Offence', backref='driver', lazy=True)

    @property
    def licence_valid(self):
        return self.licence_expiry >= date.today()


class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    vehicle_id          = db.Column(db.Integer, primary_key=True)
    number_plate        = db.Column(db.String(20), unique=True, nullable=False)
    make                = db.Column(db.String(60), nullable=False)
    model               = db.Column(db.String(60), nullable=False)
    colour              = db.Column(db.String(40), nullable=False)
    year                = db.Column(db.Integer, nullable=True)
    chassis_number      = db.Column(db.String(50), unique=True, nullable=True)
    engine_number       = db.Column(db.String(50), unique=True, nullable=True)
    registered_owner_id = db.Column(db.Integer, db.ForeignKey('drivers.driver_id'), nullable=False)
    fitness_expiry      = db.Column(db.Date, nullable=True)
    insurance_expiry    = db.Column(db.Date, nullable=True)
    vehicle_photo       = db.Column(db.String(255), nullable=True)
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)

    offences = db.relationship('Offence', backref='vehicle', lazy=True)

    @property
    def fitness_valid(self):
        return self.fitness_expiry and self.fitness_expiry >= date.today()

    @property
    def insurance_valid(self):
        return self.insurance_expiry and self.insurance_expiry >= date.today()


class OffenceType(db.Model):
    __tablename__ = 'offence_types'

    offence_type_id = db.Column(db.Integer, primary_key=True)
    code            = db.Column(db.String(10), unique=True, nullable=False)
    description     = db.Column(db.String(200), nullable=False)
    fine_amount_usd = db.Column(db.Float, nullable=False, default=0.0)
    applicable_law  = db.Column(db.String(200), nullable=True)

    offences = db.relationship('Offence', backref='offence_type', lazy=True)


class Offence(db.Model):
    __tablename__ = 'offences'

    offence_id         = db.Column(db.Integer, primary_key=True)
    vehicle_id         = db.Column(db.Integer, db.ForeignKey('vehicles.vehicle_id'), nullable=False)
    driver_id          = db.Column(db.Integer, db.ForeignKey('drivers.driver_id'), nullable=False)
    offence_type_id    = db.Column(db.Integer, db.ForeignKey('offence_types.offence_type_id'), nullable=False)
    officer_id         = db.Column(db.Integer, db.ForeignKey('officers.officer_id'), nullable=False)
    outcome            = db.Column(db.String(10), nullable=False)
    warning_expires_at = db.Column(db.DateTime, nullable=True)
    fine_paid          = db.Column(db.Boolean, default=False)
    location           = db.Column(db.String(200), nullable=True)
    notes              = db.Column(db.Text, nullable=True)
    issued_at          = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    payment = db.relationship('Payment', backref='offence', uselist=False, lazy=True)

    @property
    def warning_active(self):
        if self.outcome != 'WARNING' or not self.warning_expires_at:
            return False
        return datetime.utcnow() <= self.warning_expires_at


class Payment(db.Model):
    __tablename__ = 'payments'

    payment_id       = db.Column(db.Integer, primary_key=True)
    offence_id       = db.Column(db.Integer, db.ForeignKey('offences.offence_id'), unique=True, nullable=False)
    amount_paid      = db.Column(db.Float, nullable=False)
    payment_method   = db.Column(db.String(40), nullable=False)
    reference_number = db.Column(db.String(40), unique=True, nullable=False)
    paid_at          = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    received_by      = db.Column(db.Integer, db.ForeignKey('officers.officer_id'), nullable=False)


class AuditLog(db.Model):
    __tablename__ = 'audit_log'

    log_id       = db.Column(db.Integer, primary_key=True)
    officer_id   = db.Column(db.Integer, db.ForeignKey('officers.officer_id'), nullable=True)
    action       = db.Column(db.String(30), nullable=False)
    target_table = db.Column(db.String(40), nullable=True)
    target_id    = db.Column(db.Integer, nullable=True)
    detail       = db.Column(db.Text, nullable=True)
    ip_address   = db.Column(db.String(45), nullable=True)
    timestamp    = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
