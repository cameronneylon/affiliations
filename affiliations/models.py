from peewee import Model, CharField, DateField, ForeignKeyField, BooleanField
from affiliations.db import db

class ModelBase(Model):
    class Meta:
        database = db

class Article(ModelBase):
    title = CharField(
        help_text="Title of article.")
    doi = CharField(
        index=True,
        help_text="Digital object identifier for article.")
    date_published = DateField(
        help_text="When article was published, in YYYY(-MM(-DD)) format.")
    article_type = CharField(
        help_text="Article type obtained as text from article-type field in the article tag.")
    journal = CharField(
        help_text="The NLM TA id for the journal in which the article was published.")
    filename = CharField(
    	help_text="The filename of the JATS XML that record was parsed from.")
    related_article = CharField(null = True,
    	help_text="The DOI of a related article if relevant eg corrections.")
        
        
    def corresponding_authors(self):
        """
        Return a list of corresponding authors
        
        Note that as there may be more than one corresponding author this
        will always return a list for consistency.
        """
        return self.authors.select().where(Author.corresponding == True)


    @classmethod
    def create_or_update_by_doi(cls, args):
        """
        If an article with DOI corresponding to the 'doi' arg exists, update
        its attributes using the remaining args. If not, create it.
        """
        try:
            article = cls.get(cls.doi == args['doi'])
            for k, v in args.iteritems():
                setattr(article, k, v)
            article.save()
        except Article.DoesNotExist:
            article = Article.create(**args)
        return article      
        
class Author(ModelBase):
    article = ForeignKeyField(Article, related_name="authors")
    surname = CharField(
        help_text="Surname of author.")
    given_names = CharField(null = True,
        help_text="Given names of author.")
    affiliation_refs_raw = CharField(
        help_text="Raw contents of the affiliation fields from the XML.")
    corresponding = BooleanField(
        help_text="Is this a corresponding author?")
    
    
            
    def fullname(self):
        """
        Convenience function for returning full name in form given names + surname
        """
        return "%s %s" % (self.given_names, self.surname)
        
    def affiliations(self):
        """
        Return affiliations as a list
        """

        return [affs.address.address_raw for affs in self.affils]

    @classmethod
    def create_or_update_by_full_name(cls, args):
        """
        If an Author corresponding to full name exists, update
        its attributes using the remaining args. If not, create it.
        """
        try:
            author = cls.get(cls.fullname == "%s %s" % (args["given_names"],
                                                        args["surname"])
                            )
            for k, v in args.iteritems():
                setattr(author, k, v)
            author.save()
        except Author.DoesNotExist:
            author = Author.create(**args)
        return author       

        
class Address(ModelBase):
    article = ForeignKeyField(Article, related_name="addresses")
    affiliation_id = CharField(
        help_text="The raw affiliation id linking author to addresses.")
    address_raw = CharField(
        help_text="Raw concatenated affiliation information taken from XML.")
    country_raw = CharField(null=True,
        help_text="Country name taken from last portion of XML address info.")
    country_normalised = CharField(null=True,
        help_text="Country name normalised against ###TODO.")
        
class Affiliation(ModelBase):
    author = ForeignKeyField(Author, related_name="affils")
    address = ForeignKeyField(Address, related_name="addrs")

model_classes = [Article, Author, Address, Affiliation]

def create_db_tables():
    for klass in model_classes:
        klass.create_table()
        
def delete_all():
    for klass in model_classes:
        klass.delete().execute()      