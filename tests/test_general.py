from affiliations.models import Article, Author, Address, Affiliation
from affiliations.models import create_db_tables, delete_all
from affiliations.scrape import Plos
from affiliations.db import db
import peewee
import sqlite3
import utils

try:
    db.init(':memory:')
    create_db_tables()
except peewee.OperationalError, sqlite3.OperationalError:
    pass

def test_scrape_old_pbio_article():
    delete_all()
    test_file = "data/plos-journals-xml/PLoS_Biol/PLoS_Biol_2003_Dec_3_1(3)_e68.nxml"
    scraper = Plos(test_file)
    scraper.parse()
    doi_test = Article.select().where(Article.doi == "10.1371/journal.pbio.0000068")
    assert doi_test.count() == 1
    assert doi_test[0].corresponding_authors()[0].surname == "Froguel"
    assert len(doi_test[0].corresponding_authors()[0].affiliations()) == 2
    assert doi_test[0].authors.count() == 15
    assert doi_test[0].addresses[0].address_raw.startswith("Institute of Biology")


def test_scrape_new_pbio_article():
    delete_all()
    test_file = "data/plos-journals-xml/PLoS_Biol/PLoS_Biol_2015_Mar_31_13(3)_e1002119.nxml"
    scraper = Plos(test_file)
    scraper.parse()
    articles = [a for a in Article.select()]
    doi_test = Article.select().where(Article.doi == "10.1371/journal.pbio.1002119")
    assert doi_test.count() == 1
    assert doi_test[0].corresponding_authors()[0].surname == "Charron"
    assert len(doi_test[0].corresponding_authors()[0].affiliations()) == 5
            
def test_scrape_failing_pbio_article1():
    delete_all()
    test_file = "data/plos-journals-xml/PLoS_Biol/PLoS_Biol_2014_Sep_16_12(9)_e1001951.nxml"
    scraper = Plos(test_file)
    scraper.parse()

def test_scrape_failing_pbio_article2():
    delete_all()
    test_file = "data/plos-journals-xml/PLoS_Biol/PLoS_Biol_2009_May_5_7(5)_e1000105.nxml"
    scraper = Plos(test_file)
    article = scraper.parse()
    for author in article.authors:
        assert author.affiliations() != []
        
def test_scrape_failing_pbio_article3():
    delete_all()
    test_file = "data/plos-journals-xml/PLoS_Biol/PLoS_Biol_2013_May_7_11(5)_e1001558.nxml"
    scraper = Plos(test_file)
    article = scraper.parse()
    for author in article.authors:
        assert author.affiliations() != []
            
# For this article there is an error in the data file itself. The affiliations are 
# incorrectly tagged.
# def test_scrape_failing_pbio_article4():
#     delete_all()
#     test_file = "data/plos-journals-xml/PLoS_Biol/PLoS_Biol_2009_Feb_24_7(2)_e1000046.nxml"
#     scraper = Plos(test_file)
#     article = scraper.parse()
#     for author in article.authors:
#         assert author.affiliations() != []
    
def test_scrape_pbio_article_text_encoding_issues():
    delete_all()
    test_file = "data/plos-journals-xml/PLoS_Biol/PLoS_Biol_2004_Aug_17_2(8)_e242.nxml"
    scraper = Plos(test_file)
    article = scraper.parse()
    for author in article.authors:
        assert author.affiliations() != []  

def test_scrape_pmed_article_single_author_no_corresponding():
    delete_all()
    test_file = "data/plos-journals-xml/PLoS_Med/PLoS_Med_2005_Sep_8_2(9)_e302.nxml"
    scraper = Plos(test_file)
    article = scraper.parse()   
    
    for article in Article.select():
        if article.article_type == "research-article":
            assert article.authors.count() > 0

        else:
            if article.authors.count() == 0:
                print "Author list issue in %s type:%s" % (article.filename, 
                                                           article.article_type)


        if article.article_type == "research-article":
            assert article.authors.count() > 0
            
        else:
            if article.corresponding_authors().count() == 0 and article.authors.count() == 1:
                print "Corresponding author list issue in %s type:%s" % (article.filename, 
                                                           article.article_type)
                                                           

def test_scrape_pmed_article_badly_formed_affiliations():
    delete_all()
    test_file = "data/plos-journals-xml/PLoS_Med/PLoS_Med_2008_Mar_18_5(3)_e56.nxml"
    scraper = Plos(test_file)
    article = scraper.parse()
    for auth in article.authors:
        assert '' not in auth.affiliations()
        assert u'' not in auth.affiliations()


def test_scrape_pbio_article_with_collaboration():
    delete_all()
    test_file = "data/plos-journals-xml/PLoS_Biol/PLoS_Biol_2009_May_26_7(5)_e1000112.nxml"
    scraper = Plos(test_file)
    article = scraper.parse()
    
    affils = [auth.affiliations() for auth in article.authors if auth.given_names is not None]
    assert [u''] not in affils
    assert [u'', u''] not in affils
    assert [] not in affils         
    
def test_scrape_pgen_article_with_corresponding_issues():
    delete_all()
    test_file = "data/plos-journals-xml/PLoS_Genet/PLoS_Genet_2008_Feb_8_4(2)_e31.nxml"
    scraper = Plos(test_file)
    article = scraper.parse()
    utils.corresponding_author_integrity(verbose=True)                