from datetime import datetime as dt
from settings import load_config

import asyncpgsa
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, DateTime
)
from sqlalchemy.sql import select

metadata = MetaData()

cars = Table(
    'cars', metadata,

    Column('id', Integer, primary_key=True),
    Column('mark', String(256), nullable=False),
    Column('model', String(256), nullable=False),
    Column('generation', String(256), nullable=False),
    Column('modification', String(256), nullable=False),
    Column('year', Integer, nullable=False),
    Column('mileage', String(256), nullable=False),
    Column('state', String(128), nullable=False),
    Column('tcp_owner', Integer, nullable=False),
    Column('vin', String(2048), nullable=False),
    Column('colour', String(1024), nullable=True),
    Column('equipment', String(2048), nullable=True),
    Column('place_of_inspection', String(2048), nullable=False),
    Column('timestamp', DateTime, index=True, default=dt.today)
)

characters = Table(
    'characters', metadata,

    Column('id', Integer, primary_key=True),
    Column('car_id', Integer, ForeignKey('cars.id')),
    Column('body', String(512), nullable=False),
    Column('door', Integer, nullable=False),
    Column('engine', String(1024), nullable=False),
    Column('transmission', String(1024), nullable=False),
    Column('drive_unit', String(1024), nullable=False),
    Column('steering_wheel', String(1024), nullable=False)

)


async def add_car(conn, arr):
    print(arr)
    car = cars.insert().values(mark = arr['Марка'], model = arr['Модель'],
                               generation = arr['Поколение'], modification = arr['Модификация'],
                               year = int(arr['Год выпуска']), mileage = str(arr['Пробег']),
                               state = arr['Состояние'], tcp_owner = int(arr['Владельцев по ПТС']),
                               vin = arr['VIN или номер кузова'], colour = arr['Цвет'],
                               equipment = arr['Комплектация'], place_of_inspection = arr['Место осмотра']
                              )
    await conn.execute(car)

async def add_character(conn, arr):
    print(arr['id'])
    character = characters.insert().values( 
                                           body = arr['Тип кузова'],
                                           door = int(arr['Количество дверей']),
                                           engine = arr['Тип двигателя'],
                                           transmission = arr['Коробка передач'],
                                           drive_unit = arr['Привод'],
                                           steering_wheel = arr['Руль']
                                          )
    await conn.execute(character)

async def init_db(app):
    dsn = construct_db_url(load_config('config/user_config.toml')['database'])
    pool = await asyncpgsa.create_pool(dsn=dsn)
    app['db_pool'] = pool
    return pool


def construct_db_url(config):
    DSN = "postgresql://{host}:{port}/{database}?user={user}&password={password}"
    return DSN.format(
        user=config['DB_USER'],
        password=config['DB_PASS'],
        database=config['DB_NAME'],
        host=config['DB_HOST'],
        port=config['DB_PORT'],
    )


async def get_car_by_mark(conn, mark):
    result = await conn.fetchrow(
        cars
        .select()
        .where(cars.c.mark == mark)
    )
    return result


async def get_cars(conn):
    records = await conn.fetch(
        cars.select().order_by(cars.c.id)
    )
    return records


async def get_characters(conn):
    records = await conn.fetch(
        characters.select().order_by(characters.c.id)
    )
    return records

async def get_posts_with_joined_users(conn):
    j = posts.join(users, posts.c.user_id == users.c.id)
    stmt = select(
        [posts, users.c.username]).select_from(j).order_by(posts.c.timestamp)
    records = await conn.fetch(stmt)
    return records


