from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config.db import Base

class MainNew(Base):
    __tablename__ = 'main_new'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    body = Column(Text, nullable=True)
    link_article = Column(String, nullable=False)
    publication_date = Column(DateTime, nullable=False)
    media_id = Column(Integer, ForeignKey('main_media.id'))
    authors = Column(String, nullable=True)

class MainRssUrl(Base):
    __tablename__ = 'main_rss_url'
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    rss = Column(String, nullable=False)
    media_id = Column(Integer, ForeignKey('main_media.id'))
    media = relationship('MainMedia', back_populates='rss_urls')

class MainMedia(Base):
    __tablename__ = 'main_media'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    country = Column(String)
    web = Column(String)
    logo = Column(String)
    rss_urls = relationship('MainRssUrl', back_populates='media')
    news = relationship('MainNew', backref='media')