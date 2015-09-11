from affiliations.models import Article, Author, Address, Affiliation
from affiliations.models import create_db_tables, delete_all
from affiliations.scrape import Plos
from affiliations.db import db
import affiliations.exceptions as exceptions
import os
import os.path
import peewee
import sqlite3
import sys

try:
    db.init(':memory:')
    create_db_tables()
except peewee.OperationalError, sqlite3.OperationalError:
    pass
    

def populate_database_single_file(filepath, verbose = False):
    delete_all()
    test_file = "../data/plos-journals-xml/PLoS_Biol/PLoS_Biol_2003_Dec_3_1(3)_e68.nxml"
    scraper = Plos(test_file)
    scraper.parse()


def populate_database(directory, 
                      startnum = 0, 
                      skipnum = 100,
                      errorfile = "parse_errors",
                      verbose = False, 
                      batchsize = None):
    delete_all()
    dirlist = os.listdir(directory)
    testfiles = dirlist[startnum::skipnum]
    if batchsize:
    	testfiles = dirlist[startnum:startnum+batchsize]
    print "\nParsing %d files from %s" % (len(testfiles), directory)

    errors = []
    for i,f in enumerate(testfiles):
        if verbose: print i,f
        else:
            print '\r{0}'.format(i),
 
        filepath = os.path.join(directory, f)
        try:
            scraper = Plos(filepath)
            scraper.parse()
        except AttributeError,e:
            messg = 'AttributeError: %s %s\n' % (f,e)
            errors.append(messg)
        except KeyError, e:
            messg = 'KeyError: %s %s\n' % (f,e)
            errors.append(messg)
        except UnicodeDecodeError, e:
            messg = 'UnicodeDecodeError: %s %s\n' % (f,e)
            errors.append(messg)
        except peewee.IntegrityError, e:
            messg = 'IntegrityError: %s %s\n' % (f,e)
            errors.append(messg)
        except IndexError, e:
            messg = 'IndexError: %s %s\n' % (f,e)
            errors.append(messg)
        except exceptions.ParseError as e:
            mesg = '%s: %s\n' % (type(e), e.args)
            
    if errors != []:
        with open(os.path.join('tests', errorfile), 'a') as l:
            for error in errors:
                l.write(error)


def author_integrity(verbose=False,
                     errorfile = "parse_errors"):

    errors = []
    for article in Article.select():
        try:
            assert article.authors.count() > 0
        except AssertionError:
            mesg  = "Author integrity issue in %s type:%s\n" % (article.filename, 
                                                       article.article_type)
            if verbose: print mesg
            errors.append(mesg)

    if errors != []:
        with open(os.path.join('tests', errorfile), 'a') as l:
            for error in errors:
                l.write(error)

                                                           
def corresponding_author_integrity(verbose=False, errorfile = "parse_errors"):

    errors = []
    for article in Article.select():
        try:
            assert article.corresponding_authors().count() > 0
        except AssertionError:
            mesg = "Corresponding author list issue in %s type:%s\n" % (article.filename, 
                                                       article.article_type)
            if verbose: print mesg
            errors.append(mesg)                                      
    if errors != []:
        with open(os.path.join('tests', errorfile), 'a') as l:
            for error in errors:
                l.write(error)

def address_integrity(verbose=False, errorfile = "parse_errors"):
    errors = []
    for article in Article.select():
        try:
            affils = [auth.affiliations() for auth in article.authors if auth.given_names is not None]
            assert [u''] not in affils
            assert [u'', u''] not in affils
            assert [] not in affils
        except AssertionError, e:
            mesg = "Empty addresses in: %s type:%s\n" % (article.filename, article.article_type)
            errors.append(mesg)    
            if verbose:
                if len([auth.affiliations() for auth in article.authors]) == 0:
                    print "Address list issue in %s type:%s" % (article.filename, 
                                                               article.article_type)                              
                elif [] in [auth.affiliations() for auth in article.authors]:
                    print "Address list issue in %s type:%s" % (article.filename, 
                                                               article.article_type)
                elif [u''] in [auth.affiliations() for auth in article.authors]:
                    print "Address list issue in %s type:%s" % (article.filename, 
                                                               article.article_type)
    if errors != []:
        with open(os.path.join('tests', errorfile), 'a') as l:
            for error in errors:
                l.write(error)

def research_articles_have_at_least_one_non_empty_address(verbose=False, 
                                                          errorfile="parse_errors"):
    articles = Article.select().where(Article.article_type == "research-article")
    errors = []
    for article in articles:
        try:
            assert article.addresses.count() > 0
        except AssertionError:
            mesg = "No Address in article: %s type:%s\n" % (article.filename, article.article_type)
            if verbose: print mesg
            errors.append(mesg)

            for address in article.addresses:
                try:
                    assert address.address_raw is not u''
                    assert address.address_raw is not ''
                    assert address.affiliation_id is not u''
                    assert address.affiliation_id is not ''
                except AssertionError:
                    print "Address problem:", article.filename, address.address_raw, address.affiliation_id                

    if errors != []:
        with open(os.path.join('tests', errorfile), 'a') as l:
            for error in errors:
                l.write(error)


def whole_journal(directory, 
                  startnum = 0, 
                  skipnum = 100,
                  errorfile = "parse_errors",
                  verbose = False,
                  batchsize = None):
    populate_database(directory, startnum, skipnum, errorfile, verbose, batchsize)
    author_integrity(errorfile=errorfile)
    corresponding_author_integrity(errorfile=errorfile)
    address_integrity(errorfile=errorfile)
    research_articles_have_at_least_one_non_empty_address(errorfile=errorfile)